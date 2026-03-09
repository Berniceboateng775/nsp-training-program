"""
Vellichor AI — NLP Models Service
==================================
- Sentiment: runs locally (distilbert, small & fast)
- Emotion:   calls external API (your custom GPT-2 model on Render)
- Embeddings: runs locally (MiniLM-L6-v2 for FAISS)
"""

import os
import logging
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Config ─────────────────────────────────────────────────
EMOTION_MODEL_URL = os.getenv("EMOTION_MODEL_URL", "http://localhost:8000")

# ─── Singleton model holders ────────────────────────────────
_sentiment_pipeline = None
_embedding_model = None


def get_sentiment_pipeline():
    """Lazy-load the sentiment analysis pipeline (runs locally)."""
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
        logger.info("Loading sentiment model: distilbert-base-uncased-finetuned-sst-2-english")
        model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            top_k=None,
            device=-1
        )
        logger.info("Sentiment model loaded successfully")
    return _sentiment_pipeline


def get_embedding_model():
    """Lazy-load the sentence-transformers embedding model (runs locally)."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Embedding model loaded successfully")
    return _embedding_model


# ─── Sentiment (local) ──────────────────────────────────────

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Run sentiment analysis locally.
    Returns: {"label": "POSITIVE"/"NEGATIVE", "score": 0.99, "all_scores": {...}}
    """
    pipe = get_sentiment_pipeline()
    result = pipe(text[:512])

    scores = result[0] if isinstance(result[0], list) else result
    label_scores = {item["label"]: round(item["score"], 4) for item in scores}
    top = max(scores, key=lambda x: x["score"])

    return {
        "label": top["label"],
        "score": round(top["score"], 4),
        "all_scores": label_scores
    }


# ─── Emotions (calls your Render-hosted model) ─────────────

def analyze_emotions(text: str) -> Dict[str, Any]:
    """
    Call your custom GPT-2 emotion model hosted on Render.
    Returns: {"dominant": "Joy & Confidence", "scores": {"Joy & Confidence": 0.9, ...}}
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{EMOTION_MODEL_URL}/predict",
                json={"text": text}
            )
            response.raise_for_status()
            data = response.json()

        # Convert from model server format to our internal format
        emotion_scores = {e["label"]: e["score"] for e in data["emotions"]}
        return {
            "dominant": data["dominant"],
            "scores": emotion_scores
        }
    except Exception as e:
        logger.error(f"Emotion model API error: {e}")
        # Return a neutral fallback if the model server is down
        return {
            "dominant": "unknown",
            "scores": {}
        }


def analyze_emotions_chunks(chunks: List[str], query: str = None) -> Dict[str, Any]:
    """
    Send multiple chunks to the model server for batch analysis.
    Returns aggregate + per-chunk results.
    """
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{EMOTION_MODEL_URL}/analyze-chunks",
                json={"chunks": chunks, "query": query}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Chunk analysis API error: {e}")
        raise


# ─── Combined Analysis ──────────────────────────────────────

def analyze_text_full(text: str) -> Dict[str, Any]:
    """Run both sentiment (local) and emotion (Render API) analysis."""
    sentiment = analyze_sentiment(text)
    emotions = analyze_emotions(text)

    return {
        "sentiment": sentiment,
        "emotions": emotions
    }


# ─── Embeddings (local) ─────────────────────────────────────

def compute_embeddings(texts: List[str]) -> Any:
    model = get_embedding_model()
    return model.encode(texts, show_progress_bar=False, normalize_embeddings=True)


def compute_single_embedding(text: str) -> Any:
    model = get_embedding_model()
    return model.encode([text], normalize_embeddings=True)[0]


# ─── Model Warmup ───────────────────────────────────────────

def warmup_models():
    """Pre-load local models. Emotion model is remote, just check its health."""
    logger.info("Warming up NLP models...")
    try:
        get_sentiment_pipeline()
        get_embedding_model()
        
        # Check if emotion model server is reachable
        try:
            with httpx.Client(timeout=5.0) as client:
                r = client.get(f"{EMOTION_MODEL_URL}/health")
                if r.status_code == 200:
                    logger.info(f"Emotion model server healthy: {EMOTION_MODEL_URL}")
                else:
                    logger.warning(f"Emotion model server returned {r.status_code}")
        except Exception:
            logger.warning(f"Emotion model server not reachable at {EMOTION_MODEL_URL} — will retry on first request")
        
        logger.info("Model warmup complete")
        return True
    except Exception as e:
        logger.error(f"Model warmup failed: {e}")
        return False


def models_status() -> Dict[str, bool]:
    """Check which models are currently loaded."""
    emotion_ok = False
    try:
        with httpx.Client(timeout=3.0) as client:
            r = client.get(f"{EMOTION_MODEL_URL}/health")
            emotion_ok = r.status_code == 200
    except Exception:
        pass

    return {
        "sentiment_loaded": _sentiment_pipeline is not None,
        "emotion_model_reachable": emotion_ok,
        "embedding_loaded": _embedding_model is not None
    }
