"""Emotion & theme analysis API routes."""

from fastapi import APIRouter, Depends
from auth import get_current_user
from models import EmotionRequest, EmotionResponse
from services.huggingface import mock_emotion_analysis

router = APIRouter(prefix="/api/emotions", tags=["Emotions"])


@router.post("/analyze", response_model=EmotionResponse)
async def analyze_emotions(
    body: EmotionRequest,
    user: dict = Depends(get_current_user)
):
    """Analyze text for emotions and themes."""
    result = await mock_emotion_analysis(body.text)
    return EmotionResponse(result=result)
