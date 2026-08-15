"""API main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings, setup_logging

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 YouTube AI Assistant starting...")
    yield
    logger.info("👋 Shutting down...")

app = FastAPI(
    title="YouTube AI Assistant",
    description="Autonomous AI-powered YouTube assistant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "YouTube AI Assistant API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/v1/content/generate")
async def generate_content(video_type: str = "both"):
    return {
        "success": True,
        "message": "Content generation started",
        "type": video_type
    }

@app.post("/api/v1/content/daily")
async def generate_daily():
    return {
        "success": True,
        "message": "Daily content generation (1 Short + 1 Long-form) started"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
