"""Book recommendation API routes."""

from fastapi import APIRouter, Depends
from auth import get_current_user
from models import RecommendationRequest, RecommendationResponse
from services.huggingface import mock_recommendations

router = APIRouter(prefix="/api/recommend", tags=["Recommendations"])


@router.post("", response_model=RecommendationResponse)
async def get_recommendations(
    body: RecommendationRequest,
    user: dict = Depends(get_current_user)
):
    """Get personalized book recommendations."""
    # Merge user's saved genres with request genres
    genres = body.genres or user.get("favorite_genres", [])
    
    books = await mock_recommendations(
        query=body.query,
        genres=genres,
        mood=body.mood
    )
    
    return RecommendationResponse(books=books)


@router.get("/trending")
async def get_trending():
    """Get trending books (no auth required)."""
    books = await mock_recommendations()
    return {"books": books}
