"""API main application with all endpoints."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uuid

from config import settings, setup_logging
from workflow import ContentOrchestrator

setup_logging()
logger = logging.getLogger(__name__)

# Global state
active_tasks = {}
orchestrator = ContentOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info("🚀 YouTube AI Assistant API starting...")
    yield
    logger.info("👋 Shutting down...")


app = FastAPI(
    title="YouTube AI Assistant",
    description="Autonomous AI-powered YouTube content generation assistant",
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
    """Root endpoint."""
    return {
        "message": "YouTube AI Assistant API",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "youtube-ai-assistant"}


@app.get("/api/v1/status")
async def status():
    """Get system status."""
    return {
        "status": "operational",
        "agents": 15,
        "services": ["YouTube", "OpenAI", "ElevenLabs"],
        "active_tasks": len(active_tasks),
    }


@app.get("/api/v1/agents")
async def list_agents():
    """List all available agents."""
    agents = [
        {"name": "TrendResearchAgent", "description": "Research trending topics"},
        {"name": "TopicSelectionAgent", "description": "Select best topics"},
        {"name": "ResearchAgent", "description": "Conduct deep research"},
        {"name": "ScriptwritingAgent", "description": "Generate scripts"},
        {"name": "FactCheckingAgent", "description": "Verify facts"},
        {"name": "VoiceGenerationAgent", "description": "Generate voiceovers"},
        {"name": "VisualGenerationAgent", "description": "Generate visuals"},
        {"name": "VideoEditingAgent", "description": "Edit videos"},
        {"name": "ThumbnailAgent", "description": "Design thumbnails"},
        {"name": "SEOAgent", "description": "Optimize SEO"},
        {"name": "QualityControlAgent", "description": "Quality assurance"},
        {"name": "YouTubeUploadAgent", "description": "Upload to YouTube"},
        {"name": "AnalyticsAgent", "description": "Track analytics"},
        {"name": "OptimizationAgent", "description": "Optimize content"},
    ]
    return {"agents": agents, "total": len(agents)}


@app.post("/api/v1/content/generate-short")
async def generate_short(background_tasks: BackgroundTasks):
    """Generate short-form video (YouTube Short 30-60s)."""
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {"status": "processing", "type": "short_form"}

    async def process():
        try:
            result = await orchestrator.generate_short_form()
            active_tasks[task_id] = {"status": "completed", "result": result}
            logger.info(f"Task {task_id} completed: short-form video")
        except Exception as e:
            active_tasks[task_id] = {"status": "failed", "error": str(e)}
            logger.error(f"Task {task_id} failed: {str(e)}")

    background_tasks.add_task(process)

    return {
        "success": True,
        "task_id": task_id,
        "message": "Short-form video generation started",
        "status": "processing",
    }


@app.post("/api/v1/content/generate-long")
async def generate_long(background_tasks: BackgroundTasks):
    """Generate long-form video (15-25 minutes)."""
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {"status": "processing", "type": "long_form"}

    async def process():
        try:
            result = await orchestrator.generate_long_form()
            active_tasks[task_id] = {"status": "completed", "result": result}
            logger.info(f"Task {task_id} completed: long-form video")
        except Exception as e:
            active_tasks[task_id] = {"status": "failed", "error": str(e)}
            logger.error(f"Task {task_id} failed: {str(e)}")

    background_tasks.add_task(process)

    return {
        "success": True,
        "task_id": task_id,
        "message": "Long-form video generation started",
        "status": "processing",
    }


@app.post("/api/v1/content/generate-daily")
async def generate_daily(background_tasks: BackgroundTasks):
    """Generate daily content (1 Short + 1 Long-form)."""
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {"status": "processing", "type": "daily"}

    async def process():
        try:
            result = await orchestrator.generate_daily_content()
            active_tasks[task_id] = {"status": "completed", "result": result}
            logger.info(f"Task {task_id} completed: daily content")
        except Exception as e:
            active_tasks[task_id] = {"status": "failed", "error": str(e)}
            logger.error(f"Task {task_id} failed: {str(e)}")

    background_tasks.add_task(process)

    return {
        "success": True,
        "task_id": task_id,
        "message": "Daily content generation (1 Short + 1 Long-form) started",
        "status": "processing",
    }


@app.get("/api/v1/task/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and result."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = active_tasks[task_id]
    return {
        "task_id": task_id,
        "status": task.get("status"),
        "type": task.get("type"),
        "result": task.get("result"),
        "error": task.get("error"),
    }


@app.get("/api/v1/tasks")
async def list_tasks():
    """List all tasks."""
    return {
        "tasks": active_tasks,
        "count": len(active_tasks),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
