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

# ─── Positive/negative emotion mappings ─────────────────────
POSITIVE_LABELS = {
    "joy", "love", "gratitude", "amusement", "approval", "caring",
    "desire", "excitement", "optimism", "pride", "relief", "admiration",
    "curiosity", "hope", "confidence", "positive", "happiness",
    "joy & confidence", "love & tenderness", "surprise & curiosity",
}
NEGATIVE_LABELS = {
    "anger", "annoyance", "disappointment", "disapproval", "disgust",
    "embarrassment", "fear", "grief", "nervousness", "remorse",
    "sadness", "negative", "frustration", "anxiety",
    "anger & frustration", "fear & anxiety", "sadness & grief",
}


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Lightweight sentiment analysis — derives sentiment from emotion keywords.
    No ML model needed, so no memory overhead.
    """
    text_lower = text.lower().strip()

    pos_match = any(label in text_lower for label in POSITIVE_LABELS)
    neg_match = any(label in text_lower for label in NEGATIVE_LABELS)

    if pos_match and not neg_match:
        return {"label": "POSITIVE", "score": 0.90, "all_scores": {"POSITIVE": 0.90, "NEGATIVE": 0.10}}
    elif neg_match and not pos_match:
        return {"label": "NEGATIVE", "score": 0.90, "all_scores": {"POSITIVE": 0.10, "NEGATIVE": 0.90}}
    elif pos_match and neg_match:
        return {"label": "MIXED", "score": 0.60, "all_scores": {"POSITIVE": 0.50, "NEGATIVE": 0.50}}
    else:
        return {"label": "NEUTRAL", "score": 0.70, "all_scores": {"POSITIVE": 0.50, "NEGATIVE": 0.50}}


# ─── Emotions (calls your Render-hosted model) ─────────────

def analyze_emotions(text: str, situation: str = "") -> Dict[str, Any]:
    """
    Call your custom GPT-2 emotion model hosted on Render.
    Returns: {"dominant": "Joy & Confidence", "scores": {"Joy & Confidence": 0.9, ...}}
    """
    try:
        with httpx.Client(timeout=90.0) as client:
            response = client.post(
                f"{EMOTION_MODEL_URL}/predict",
                json={"text": text, "situation": situation or None}
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
        with httpx.Client(timeout=120.0) as client:
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

def analyze_text_full(text: str, situation: str = "") -> Dict[str, Any]:
    """Run both emotion (Render API) and sentiment (local) analysis.
    
    Sentiment is derived from the emotion model's dominant label,
    not the raw text. This prevents contradictions like
    'Joy & Confidence' being labeled NEGATIVE.
    """
    # Step 1: Get emotions from your custom GPT-2 model
    emotions = analyze_emotions(text, situation=situation)
    
    # Step 2: Feed the dominant emotion label into DistilBERT for sentiment
    # e.g. "Joy & Confidence" → POSITIVE, "Anger" → NEGATIVE
    dominant = emotions.get("dominant", "unknown")
    sentiment = analyze_sentiment(dominant) if dominant != "unknown" else analyze_sentiment(text)

    return {
        "sentiment": sentiment,
        "emotions": emotions
    }


# ─── Embeddings (lazy-loaded, only when user uploads a document) ──

_embedding_model = None


def _get_embedding_model():
    """Lazy-load the sentence-transformers embedding model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Embedding model loaded successfully")
    return _embedding_model


def compute_embeddings(texts: List[str]) -> Any:
    model = _get_embedding_model()
    return model.encode(texts, show_progress_bar=False, normalize_embeddings=True)


def compute_single_embedding(text: str) -> Any:
    model = _get_embedding_model()
    return model.encode([text], normalize_embeddings=True)[0]


# ─── Model Status ───────────────────────────────────────────

def warmup_models():
    """No-op — models lazy-load on demand to stay within memory limits."""
    logger.info("Model warmup skipped (memory-constrained mode)")
    return True


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
        "sentiment_loaded": True,  # rule-based, always available
        "emotion_model_reachable": emotion_ok,
        "embedding_loaded": _embedding_model is not None
    }
