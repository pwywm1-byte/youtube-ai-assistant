"""Updated API main application with complete endpoints."""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import Optional
import asyncio

from config import settings, setup_logging
from workflow.orchestrator import ContentOrchestrator

setup_logging()
logger = logging.getLogger(__name__)

orchestrateur = ContentOrchestrator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 YouTube AI Assistant starting...")
    yield
    logger.info("👋 Shutting down...")

app = FastAPI(
    title="YouTube AI Assistant API",
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

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "YouTube AI Assistant API",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0",
    }

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "youtube-ai-assistant"}

# Content Generation Endpoints
@app.post("/api/v1/content/generate")
async def generate_content(
    video_type: str = Query("both", description="Type of video: short, long_form, or both"),
    background_tasks: BackgroundTasks = None,
):
    """Generate YouTube content (Short and/or Long-form video)."""
    try:
        if video_type not in ["short", "long_form", "both"]:
            raise HTTPException(status_code=400, detail="Invalid video_type")
        
        logger.info(f"Starting content generation: {video_type}")
        
        # Run in background if requested
        if background_tasks:
            background_tasks.add_task(orchestrateur.generate_complete_video, video_type)
            return {
                "success": True,
                "message": f"Content generation ({video_type}) started in background",
                "type": video_type,
            }
        else:
            result = await orchestrateur.generate_complete_video(video_type)
            return result
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/content/daily")
async def generate_daily(background_tasks: BackgroundTasks = None):
    """Generate daily content (1 Short + 1 Long-form video)."""
    try:
        logger.info("Starting daily content generation")
        
        if background_tasks:
            background_tasks.add_task(orchestrateur.generate_daily_content)
            return {
                "success": True,
                "message": "Daily content generation (1 Short + 1 Long-form) started in background",
            }
        else:
            result = await orchestrateur.generate_daily_content()
            return result
    except Exception as e:
        logger.error(f"Error generating daily content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent Status Endpoints
@app.get("/api/v1/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    try:
        agents = [
            orchestrateur.trend_agent,
            orchestrateur.topic_agent,
            orchestrateur.research_agent,
            orchestrateur.script_agent,
            orchestrateur.fact_check_agent,
            orchestrateur.voice_agent,
            orchestrateur.visual_agent,
            orchestrateur.video_agent,
            orchestrateur.thumbnail_agent,
            orchestrateur.seo_agent,
            orchestrateur.quality_agent,
            orchestrateur.upload_agent,
            orchestrateur.analytics_agent,
        ]
        
        return {
            "success": True,
            "agents": [agent.get_status() for agent in agents],
        }
    except Exception as e:
        logger.error(f"Error getting agents status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get status of specific agent."""
    try:
        agent_map = {
            "trend": orchestrateur.trend_agent,
            "topic": orchestrateur.topic_agent,
            "research": orchestrateur.research_agent,
            "script": orchestrateur.script_agent,
            "fact_check": orchestrateur.fact_check_agent,
            "voice": orchestrateur.voice_agent,
            "visual": orchestrateur.visual_agent,
            "video": orchestrateur.video_agent,
            "thumbnail": orchestrateur.thumbnail_agent,
            "seo": orchestrateur.seo_agent,
            "quality": orchestrateur.quality_agent,
            "upload": orchestrateur.upload_agent,
            "analytics": orchestrateur.analytics_agent,
        }
        
        agent = agent_map.get(agent_name)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
        
        return {"success": True, "agent": agent.get_status()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Configuration Endpoints
@app.get("/api/v1/config")
async def get_config():
    """Get application configuration (non-sensitive)."""
    try:
        return {
            "success": True,
            "config": {
                "api_host": settings.API_HOST,
                "api_port": settings.API_PORT,
                "api_debug": settings.API_DEBUG,
                "log_level": settings.LOG_LEVEL,
                "development_mode": settings.DEVELOPMENT_MODE,
                "video_quality": settings.VIDEO_QUALITY,
                "video_bitrate": settings.VIDEO_BITRATE,
                "audio_bitrate": settings.AUDIO_BITRATE,
                "publish_short_time": settings.PUBLISH_SHORT_TIME,
                "publish_longform_time": settings.PUBLISH_LONGFORM_TIME,
                "publish_timezone": settings.PUBLISH_TIMEZONE,
            },
        }
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# System Endpoints
@app.get("/api/v1/system/info")
async def system_info():
    """Get system information."""
    try:
        return {
            "success": True,
            "system": {
                "service_name": "YouTube AI Assistant",
                "version": "1.0.0",
                "environment": "development" if settings.DEVELOPMENT_MODE else "production",
                "log_level": settings.LOG_LEVEL,
                "features": {
                    "auto_publish": settings.ENABLE_AUTO_PUBLISH,
                    "analytics_tracking": settings.ENABLE_ANALYTICS_TRACKING,
                    "auto_optimization": settings.ENABLE_AUTO_OPTIMIZATION,
                    "fact_checking": settings.ENABLE_FACT_CHECKING,
                    "quality_control": settings.ENABLE_QUALITY_CONTROL,
                },
            },
        }
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
