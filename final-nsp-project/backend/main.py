"""
Vellichor AI — FastAPI Backend Entry Point
==========================================
An intelligent reading companion powered by HuggingFace models.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from auth import register_user, login_user
from models import UserRegister, UserLogin, TokenResponse
from routes import chat, recommend, emotions, profile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and warm up ML models on startup."""
    await init_db()
    
    # Skip ML model warmup on Render free tier (512MB limit)
    # Models will lazy-load on first request if needed
    logger.info("Skipping eager model warmup (memory-constrained environment)")
    
    yield


app = FastAPI(
    title="Vellichor AI",
    description="HuggingFace-powered intelligent reading companion with sentiment analysis, emotion detection, and document understanding.",
    version="2.0.0",
    lifespan=lifespan
)

# CORS — allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vellichor-puce.vercel.app",
        "https://vellichor.vercel.app",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5500",
    ],
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


@app.get("/api/models/status", tags=["System"])
async def model_status():
    """Check which ML models are currently loaded."""
    try:
        from services.nlp_models import models_status
        status = models_status()
        return {"status": "ok", "models": status}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


# ─── Include Route Modules ─────────────────────────────────

app.include_router(chat.router)
app.include_router(recommend.router)
app.include_router(emotions.router)
app.include_router(profile.router)
