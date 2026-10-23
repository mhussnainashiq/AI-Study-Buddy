
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.connection import Base, engine
from app.database import models
from app.routers import (
    documents,
    summaries,
    flashcards,
    quizzes,
    tutor,
    progress,
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create the FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered study assistant API",
)

# Allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
for router in (
    documents.router,
    summaries.router,
    flashcards.router,
    quizzes.router,
    tutor.router,
    progress.router,
):
    app.include_router(router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to AI Study Buddy API",
        "docs": "/docs",
        "health": "/api/health",
    }


# Health check endpoint
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "ai_configured": bool(settings.openai_api_key),
    }


# Handle unexpected errors
@app.exception_handler(Exception)
async def unexpected_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )
