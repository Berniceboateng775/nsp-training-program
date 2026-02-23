"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ─── Auth Models ───────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    favorite_genres: List[str] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    favorite_genres: List[str]
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Chat Models ───────────────────────────────────────────

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    conversation_id: str


# ─── Recommendation Models ────────────────────────────────

class RecommendationRequest(BaseModel):
    query: Optional[str] = None
    genres: Optional[List[str]] = None
    mood: Optional[str] = None

class BookRecommendation(BaseModel):
    title: str
    author: str
    genre: str
    description: str
    reason: str
    rating: float
    cover_url: Optional[str] = None

class RecommendationResponse(BaseModel):
    books: List[BookRecommendation]


# ─── Emotion Analysis Models ──────────────────────────────

class EmotionRequest(BaseModel):
    text: str

class EmotionResult(BaseModel):
    emotions: dict  # {"joy": 0.8, "sadness": 0.1, ...}
    themes: List[str]
    summary: str

class EmotionResponse(BaseModel):
    result: EmotionResult


# ─── Profile Models ───────────────────────────────────────

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    favorite_genres: Optional[List[str]] = None

class ReadingHistoryItem(BaseModel):
    book_title: str
    added_at: str
