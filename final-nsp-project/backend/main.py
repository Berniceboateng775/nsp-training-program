"""
Vellichor AI — FastAPI Backend Entry Point
==========================================
An intelligent reading companion powered by GPT models.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from auth import register_user, login_user
from models import UserRegister, UserLogin, TokenResponse
from routes import chat, recommend, emotions, profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database indexes on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Vellichor AI",
    description="GPT-powered intelligent reading companion with personalized recommendations, conversational AI, and emotion-aware book analysis.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Auth Routes ───────────────────────────────────────────

@app.post("/api/register", response_model=TokenResponse, tags=["Auth"])
async def register(body: UserRegister):
    """Register a new user account."""
    result = await register_user(
        name=body.name,
        email=body.email,
        password=body.password,
        favorite_genres=body.favorite_genres
    )
    return result


@app.post("/api/login", response_model=TokenResponse, tags=["Auth"])
async def login(body: UserLogin):
    """Authenticate and receive access token."""
    result = await login_user(email=body.email, password=body.password)
    return result


@app.get("/api/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "Vellichor AI"}


# ─── Include Route Modules ─────────────────────────────────

app.include_router(chat.router)
app.include_router(recommend.router)
app.include_router(emotions.router)
app.include_router(profile.router)
