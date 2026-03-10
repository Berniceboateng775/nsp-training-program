"""
Vellichor Emotion Detector — FastAPI Model Server
===================================================
Serves the custom GPT-2 emotion detection model (7 labels).
Downloads model from HuggingFace Hub on startup.

Endpoints:
  POST /predict       — classify single text
  POST /analyze-chunks — classify multiple chunks + aggregate
  GET  /health        — status check
"""

import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────
MODEL_REPO = os.getenv("MODEL_REPO", "Bernice775/vellichor-emotion-detector")

# ─── Singleton model holder ─────────────────────────
_classifier = None


def load_model():
    """Download and load the emotion classifier from HuggingFace Hub."""
    global _classifier
    if _classifier is None:
        import gc
        import torch
        from transformers import pipeline
        
        logger.info(f"Loading model from HuggingFace: {MODEL_REPO}")
        
        # Load pipeline directly — avoids keeping separate model/tokenizer copies in memory
        _classifier = pipeline(
            "text-classification",
            model=MODEL_REPO,
            tokenizer=MODEL_REPO,
            top_k=None,
            device=-1,
            torch_dtype=torch.float16,
            model_kwargs={"low_cpu_mem_usage": True}
        )
        
        # Aggressively free any temporary loading memory
        gc.collect()
        logger.info("Model loaded successfully!")
    return _classifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup."""
    logger.info("Starting model server...")
    try:
        load_model()
    except Exception as e:
        logger.error(f"Model load failed: {e}")
    yield


app = FastAPI(
    title="Vellichor Emotion Detector",
    description="Custom GPT-2 emotion classifier with 7 literary emotion categories",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request/Response Models ─────────────────────────

class PredictRequest(BaseModel):
    text: str
    situation: Optional[str] = None  # context makes predictions much more accurate

class ChunksRequest(BaseModel):
    chunks: List[str]
    query: Optional[str] = None

class EmotionScore(BaseModel):
    label: str
    score: float

class PredictResponse(BaseModel):
    emotions: List[EmotionScore]
    dominant: str
    dominant_score: float

class AggregateResponse(BaseModel):
    per_chunk: List[PredictResponse]
    aggregate_emotions: dict
    dominant_emotion: str
    summary: str
    total_chunks: int


# ─── Endpoints ───────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model": MODEL_REPO,
        "model_loaded": _classifier is not None
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(body: PredictRequest):
    """Classify a single text and return all 7 emotion scores."""
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    classifier = load_model()
    
    try:
        # Format input the way the model was trained:
        # "Situation: [context] Dialogue: [text]"
        formatted = _format_input(text, body.situation)
        
        results = classifier(formatted[:3000])
        scores = results[0] if isinstance(results[0], list) else results
        
        sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)
        
        return PredictResponse(
            emotions=[EmotionScore(label=s["label"], score=round(s["score"], 4)) for s in sorted_scores],
            dominant=sorted_scores[0]["label"],
            dominant_score=round(sorted_scores[0]["score"], 4)
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/analyze-chunks", response_model=AggregateResponse)
async def analyze_chunks(body: ChunksRequest):
    """Analyze multiple text chunks and return per-chunk + aggregate results."""
    if not body.chunks:
        raise HTTPException(status_code=400, detail="No chunks provided")
    
    classifier = load_model()
    
    try:
        per_chunk = []
        all_emotions = {}
        
        for chunk in body.chunks:
            formatted = _format_input(chunk, body.query)
            results = classifier(formatted[:3000])
            scores = results[0] if isinstance(results[0], list) else results
            sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)
            
            per_chunk.append(PredictResponse(
                emotions=[EmotionScore(label=s["label"], score=round(s["score"], 4)) for s in sorted_scores],
                dominant=sorted_scores[0]["label"],
                dominant_score=round(sorted_scores[0]["score"], 4)
            ))
            
            # Accumulate for aggregation
            for s in scores:
                all_emotions[s["label"]] = all_emotions.get(s["label"], 0) + s["score"]
        
        # Average emotions
        n = len(body.chunks)
        avg_emotions = {k: round(v / n, 4) for k, v in all_emotions.items()}
        dominant = max(avg_emotions, key=avg_emotions.get)
        
        # Generate summary
        summary = _build_summary(dominant, avg_emotions, n, body.query)
        
        return AggregateResponse(
            per_chunk=per_chunk,
            aggregate_emotions=avg_emotions,
            dominant_emotion=dominant,
            summary=summary,
            total_chunks=n
        )
    except Exception as e:
        logger.error(f"Chunk analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def _format_input(text: str, situation: str = None) -> str:
    """Format input the way the model was trained: 'Situation: ... Dialogue: ...'
    
    Without this format, the model hits the '57% wall' — it can't distinguish
    emotions from ambiguous text alone. The context-aware format is what pushed
    accuracy from 57% to 79%.
    """
    text = text.strip()
    # If the text already has the format, don't double-wrap
    if text.lower().startswith('situation:'):
        return text
    
    if situation:
        return f"Situation: {situation} Dialogue: {text}"
    else:
        # Use a generic situation when none provided
        return f"Situation: A person is expressing their thoughts and feelings. Dialogue: {text}"


def _build_summary(dominant: str, emotions: dict, n: int, query: str = None) -> str:
    """Generate a human-readable analysis summary."""
    descriptions = {
        "Joy & Confidence": "warmth, positivity, and triumphant energy",
        "Sadness": "contemplative melancholy and emotional depth",
        "Anger": "fierce intensity, conflict, and passionate conviction",
        "Fear & Tension": "suspenseful unease and gripping apprehension",
        "Connection & Trust": "deep emotional bonds, intimacy, and belonging",
        "Vulnerability": "raw honesty, exposure, and tender fragility",
        "Suspense & Reflection": "thoughtful introspection and mysterious undertones"
    }
    
    desc = descriptions.get(dominant, f"complex undertones of {dominant}")
    score_pct = f"{emotions.get(dominant, 0):.0%}"
    
    sorted_emos = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
    secondary = sorted_emos[1][0] if len(sorted_emos) > 1 else None
    
    context = f"for your query '{query}' " if query else ""
    
    summary = (
        f"Across {n} analyzed passages {context}the dominant emotion is "
        f"**{dominant}** ({score_pct} confidence), characterized by {desc}."
    )
    
    if secondary:
        sec_desc = descriptions.get(secondary, secondary)
        summary += f" A secondary thread of **{secondary}** adds layers of {sec_desc}."
    
    return summary


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
