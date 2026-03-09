"""
Vellichor AI — NLP Models Service
==================================
Lazy-loads HuggingFace models for sentiment analysis, emotion detection,
and sentence embeddings. Models are loaded once and cached as singletons.

Models used:
  - Sentiment: distilbert-base-uncased-finetuned-sst-2-english
  - Emotion:   nateraw/bert-base-uncased-emotion
  - Embeddings: sentence-transformers/all-MiniLM-L6-v2
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# ─── Singleton model holders ────────────────────────────────

_sentiment_pipeline = None
_emotion_pipeline = None
_embedding_model = None


def get_sentiment_pipeline():
    """Lazy-load the sentiment analysis pipeline."""
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
            device=-1  # CPU
        )
        logger.info("Sentiment model loaded successfully")
    return _sentiment_pipeline


def get_emotion_pipeline():
    """Lazy-load the emotion classification pipeline."""
    global _emotion_pipeline
    if _emotion_pipeline is None:
        from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
        logger.info("Loading emotion model: nateraw/bert-base-uncased-emotion")
        model_name = "nateraw/bert-base-uncased-emotion"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _emotion_pipeline = pipeline(
            "text-classification",
            model=model,
            tokenizer=tokenizer,
            top_k=None,
            device=-1  # CPU
        )
        logger.info("Emotion model loaded successfully")
    return _emotion_pipeline


def get_embedding_model():
    """Lazy-load the sentence-transformers embedding model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        logger.info("Embedding model loaded successfully")
    return _embedding_model


# ─── Analysis Functions ─────────────────────────────────────

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Run sentiment analysis on a text string.
    Returns: {"label": "POSITIVE"/"NEGATIVE", "score": 0.99, "all_scores": {...}}
    """
    pipe = get_sentiment_pipeline()
    # Truncate to 512 tokens (model limit)
    result = pipe(text[:512])

    # result is [[{label, score}, ...]] when top_k=None
    scores = result[0] if isinstance(result[0], list) else result
    label_scores = {item["label"]: round(item["score"], 4) for item in scores}
    top = max(scores, key=lambda x: x["score"])

    return {
        "label": top["label"],
        "score": round(top["score"], 4),
        "all_scores": label_scores
    }


def analyze_emotions(text: str) -> Dict[str, Any]:
    """
    Run emotion classification on a text string.
    Returns: {"dominant": "joy", "scores": {"joy": 0.9, "sadness": 0.02, ...}}
    """
    pipe = get_emotion_pipeline()
    result = pipe(text[:512])

    scores = result[0] if isinstance(result[0], list) else result
    emotion_scores = {item["label"]: round(item["score"], 4) for item in scores}
    dominant = max(scores, key=lambda x: x["score"])

    return {
        "dominant": dominant["label"],
        "scores": emotion_scores
    }


def analyze_text_full(text: str) -> Dict[str, Any]:
    """
    Run both sentiment and emotion analysis on a text.
    Returns combined result.
    """
    sentiment = analyze_sentiment(text)
    emotions = analyze_emotions(text)

    return {
        "sentiment": sentiment,
        "emotions": emotions
    }


def compute_embeddings(texts: List[str]) -> Any:
    """
    Compute sentence embeddings for a list of text chunks.
    Returns numpy array of shape (n_texts, 384).
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings


def compute_single_embedding(text: str) -> Any:
    """Compute embedding for a single text query."""
    model = get_embedding_model()
    return model.encode([text], normalize_embeddings=True)[0]


# ─── Model Warmup ───────────────────────────────────────────

def warmup_models():
    """Pre-load all models so first request isn't slow."""
    logger.info("Warming up NLP models...")
    try:
        get_sentiment_pipeline()
        get_emotion_pipeline()
        get_embedding_model()
        logger.info("All NLP models warmed up successfully")
        return True
    except Exception as e:
        logger.error(f"Model warmup failed: {e}")
        return False


def models_status() -> Dict[str, bool]:
    """Check which models are currently loaded."""
    return {
        "sentiment_loaded": _sentiment_pipeline is not None,
        "emotion_loaded": _emotion_pipeline is not None,
        "embedding_loaded": _embedding_model is not None
    }
