"""
Vellichor AI — FastAPI Backend Entry Point
==========================================
An intelligent reading companion powered by HuggingFace models.
"""

import logging
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global Exception Handler (ensures CORS headers on errors) ────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and return proper JSON with CORS headers."""
    logger.error(f"Unhandled error on {request.method} {request.url}: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
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
