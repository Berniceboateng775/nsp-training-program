"""
Emotion & Sentiment Analysis API routes.
Supports both text input and PDF file upload.
"""

import uuid
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from auth import get_current_user
from models import (
    EmotionRequest, EmotionResponse, EmotionResult,
    TextAnalysisResponse, SentimentResult,
    FileAnalysisResponse, ChunkAnalysis, FileUploadResponse
)
from services.nlp_models import analyze_sentiment, analyze_emotions, analyze_text_full
from services.pdf_processor import (
    process_document, get_session_chunks, extract_text_from_pdf,
    extract_text_from_txt, chunk_text, retrieve_context, session_exists
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/emotions", tags=["Emotions"])


# ─── Text Analysis (real models) ───────────────────────────

@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text_endpoint(
    body: EmotionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Analyze pasted text for sentiment and emotions using real HuggingFace models.
    - Sentiment: distilbert-base-uncased-finetuned-sst-2-english
    - Emotion:  nateraw/bert-base-uncased-emotion
    """
    text = body.text.strip()
    if len(text) < 10:
        raise HTTPException(status_code=400, detail="Text must be at least 10 characters")

    try:
        result = analyze_text_full(text)
        return TextAnalysisResponse(
            sentiment=SentimentResult(**result["sentiment"]),
            emotions=result["emotions"]["scores"],
            dominant_emotion=result["emotions"]["dominant"]
        )
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ─── File Upload + Analysis ────────────────────────────────

@router.post("/analyze-file", response_model=FileAnalysisResponse)
async def analyze_file_endpoint(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Upload a PDF or TXT file, extract text, chunk it, and run
    sentiment + emotion analysis on each chunk.
    Returns per-chunk and aggregate results.
    """
    # Validate file type
    filename = file.filename or "unknown"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext not in ("pdf", "txt", "text"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PDF or TXT files."
        )

    # Read file
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        # Extract text
        if ext == "pdf":
            full_text = extract_text_from_pdf(content)
        else:
            full_text = extract_text_from_txt(content)

        if len(full_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Document contains too little text to analyze"
            )

        # Chunk the text
        chunks = chunk_text(full_text, chunk_size=600, chunk_overlap=100)

        # Analyze each chunk
        chunk_results = []
        all_sentiments = []
        all_emotions = {}

        for i, chunk in enumerate(chunks):
            analysis = analyze_text_full(chunk)

            sentiment = analysis["sentiment"]
            emotions = analysis["emotions"]

            chunk_results.append(ChunkAnalysis(
                chunk_text=chunk[:200] + "..." if len(chunk) > 200 else chunk,
                chunk_index=i,
                sentiment=SentimentResult(**sentiment),
                emotions=emotions["scores"],
                dominant_emotion=emotions["dominant"]
            ))

            # Accumulate for aggregation
            all_sentiments.append(sentiment)
            for emo, score in emotions["scores"].items():
                all_emotions[emo] = all_emotions.get(emo, 0) + score

        # Compute aggregates
        n = len(chunks)
        avg_emotions = {k: round(v / n, 4) for k, v in all_emotions.items()}
        dominant_emotion = max(avg_emotions, key=avg_emotions.get)

        # Aggregate sentiment
        pos_avg = sum(s["all_scores"].get("POSITIVE", 0) for s in all_sentiments) / n
        neg_avg = sum(s["all_scores"].get("NEGATIVE", 0) for s in all_sentiments) / n
        agg_label = "POSITIVE" if pos_avg >= neg_avg else "NEGATIVE"
        agg_score = max(pos_avg, neg_avg)

        # Generate summary
        summary = _generate_analysis_summary(agg_label, dominant_emotion, avg_emotions, n)

        return FileAnalysisResponse(
            filename=filename,
            total_chunks=n,
            chunks=chunk_results,
            aggregate_sentiment=SentimentResult(
                label=agg_label,
                score=round(agg_score, 4),
                all_scores={"POSITIVE": round(pos_avg, 4), "NEGATIVE": round(neg_avg, 4)}
            ),
            aggregate_emotions=avg_emotions,
            dominant_emotion=dominant_emotion,
            summary=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")


# ─── Document Upload for Chat Context ─────────────────────

@router.post("/upload", response_model=FileUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Upload a document and index it with FAISS for later retrieval.
    Used by the chatbot to answer questions about uploaded books.
    """
    filename = file.filename or "unknown"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext not in ("pdf", "txt", "text"):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        session_id = user.get("id", str(uuid.uuid4()))
        result = process_document(session_id, content, filename)
        return FileUploadResponse(**result)
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


# ─── Query + Analyze (FAISS retrieval → analyze relevant chunks) ──

@router.post("/query-analyze")
async def query_and_analyze(
    body: EmotionRequest,
    user: dict = Depends(get_current_user)
):
    """
    Retrieve relevant chunks from an indexed PDF using FAISS,
    then run sentiment + emotion analysis on those chunks only (max 10).
    Much faster than analyzing the entire document.
    """
    user_id = user.get("id", "")
    query = body.text.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Please describe what to analyze")

    if not session_exists(user_id):
        raise HTTPException(
            status_code=400,
            detail="No document loaded. Please upload a PDF first."
        )

    try:
        # Retrieve top 10 relevant chunks
        results = retrieve_context(user_id, query, top_k=10)

        if not results:
            raise HTTPException(status_code=400, detail="No relevant passages found for your query")

        # Analyze each retrieved chunk
        chunk_results = []
        all_emotions = {}

        for i, result in enumerate(results):
            chunk_text = result["chunk"]
            analysis = analyze_text_full(chunk_text)

            sentiment = analysis["sentiment"]
            emotions = analysis["emotions"]

            chunk_results.append({
                "chunk_text": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                "chunk_index": i,
                "similarity_score": result["score"],
                "sentiment": sentiment,
                "emotions": emotions["scores"],
                "dominant_emotion": emotions["dominant"]
            })

            for emo, score in emotions["scores"].items():
                all_emotions[emo] = all_emotions.get(emo, 0) + score

        # Compute aggregates
        n = len(results)
        avg_emotions = {k: round(v / n, 4) for k, v in all_emotions.items()}
        dominant_emotion = max(avg_emotions, key=avg_emotions.get)

        # Aggregate sentiment
        pos_avg = sum(c["sentiment"]["all_scores"].get("POSITIVE", 0) for c in chunk_results) / n
        neg_avg = sum(c["sentiment"]["all_scores"].get("NEGATIVE", 0) for c in chunk_results) / n
        agg_label = "POSITIVE" if pos_avg >= neg_avg else "NEGATIVE"

        summary = _generate_analysis_summary(agg_label, dominant_emotion, avg_emotions, n)

        return {
            "sentiment": {
                "label": agg_label,
                "score": round(max(pos_avg, neg_avg), 4),
                "all_scores": {"POSITIVE": round(pos_avg, 4), "NEGATIVE": round(neg_avg, 4)}
            },
            "emotions": avg_emotions,
            "dominant_emotion": dominant_emotion,
            "summary": summary,
            "chunks_analyzed": n,
            "query": query
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query-analyze error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ─── Helpers ───────────────────────────────────────────────

def _generate_analysis_summary(
    sentiment_label: str,
    dominant_emotion: str,
    emotions: dict,
    num_chunks: int
) -> str:
    """Generate a human-readable summary of the analysis."""
    emotion_descriptions = {
        "joy": "warmth, positivity, and uplifting themes",
        "sadness": "contemplative melancholy and reflective undertones",
        "anger": "intensity, conflict, and passionate conviction",
        "fear": "tension, unease, and atmospheric suspense",
        "surprise": "unexpected twists and revelatory moments",
        "love": "tenderness, connection, and deep emotional bonds"
    }

    tone = "positive and uplifting" if sentiment_label == "POSITIVE" else "somber and reflective"
    emotion_desc = emotion_descriptions.get(
        dominant_emotion,
        f"complex emotional undertones centered on {dominant_emotion}"
    )

    # Find secondary emotions
    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
    secondary = [e[0] for e in sorted_emotions[1:3]] if len(sorted_emotions) > 1 else []

    summary = (
        f"Across {num_chunks} analyzed passages, this text carries a predominantly "
        f"{tone} tone with {emotion_desc}. "
        f"The dominant emotion detected is **{dominant_emotion}** "
        f"({emotions.get(dominant_emotion, 0):.0%} average confidence)."
    )

    if secondary:
        summary += (
            f" Secondary emotional threads include **{secondary[0]}** and "
            f"**{secondary[1] if len(secondary) > 1 else 'nuanced complexity'}**, "
            f"creating a rich, multi-layered emotional landscape."
        )

    return summary
