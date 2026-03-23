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
    situation: str = ""

class EmotionResult(BaseModel):
    emotions: dict  # {"joy": 0.8, "sadness": 0.1, ...}
    themes: List[str]
    summary: str

class SentimentResult(BaseModel):
    label: str         # "POSITIVE" or "NEGATIVE"
    score: float       # confidence 0-1
    all_scores: dict   # {"POSITIVE": 0.99, "NEGATIVE": 0.01}

class ChunkAnalysis(BaseModel):
    chunk_text: str
    chunk_index: int
    sentiment: SentimentResult
    emotions: dict     # {"joy": 0.9, "sadness": 0.02, ...}
    dominant_emotion: str

class FileAnalysisResponse(BaseModel):
    filename: str
    total_chunks: int
    chunks: List[ChunkAnalysis]
    aggregate_sentiment: SentimentResult
    aggregate_emotions: dict
    dominant_emotion: str
    summary: str

class EmotionResponse(BaseModel):
    result: EmotionResult

class TextAnalysisResponse(BaseModel):
    sentiment: SentimentResult
    emotions: dict
    dominant_emotion: str

class FileUploadResponse(BaseModel):
    filename: str
    total_characters: int
    total_chunks: int
    status: str


# ─── Profile Models ───────────────────────────────────────

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    favorite_genres: Optional[List[str]] = None

class ReadingHistoryItem(BaseModel):
    book_title: str
    added_at: str
