"""Application settings and configuration."""

import os
import logging
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = False
    API_WORKERS: int = 4
    SECRET_KEY: str = "change-this-in-production"

    # Database
    DATABASE_URL: str = "postgresql://youtube_ai:password@localhost:5432/youtube_ai_db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # YouTube
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_CHANNEL_ID: Optional[str] = None
    YOUTUBE_REFRESH_TOKEN: Optional[str] = None
    YOUTUBE_SCOPES: str = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"

    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    # Asset APIs
    UNSPLASH_ACCESS_KEY: Optional[str] = None
    PEXELS_API_KEY: Optional[str] = None

    # Video Settings
    VIDEO_QUALITY: str = "1080p"
    VIDEO_BITRATE: str = "8000k"
    AUDIO_BITRATE: str = "192k"
    SHORT_DURATION_MIN: int = 30
    SHORT_DURATION_MAX: int = 60
    LONG_DURATION_MIN: int = 900
    LONG_DURATION_MAX: int = 1500

    # Publishing
    PUBLISH_SHORT_TIME: str = "09:00"
    PUBLISH_LONGFORM_TIME: str = "18:00"
    PUBLISH_TIMEZONE: str = "UTC"

    # Storage
    STORAGE_PATH: str = "./storage"
    VIDEOS_PATH: str = "./storage/videos"
    THUMBNAILS_PATH: str = "./storage/thumbnails"
    SCRIPTS_PATH: str = "./storage/scripts"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "./logs"

    # Development
    DEVELOPMENT_MODE: bool = False
    DEBUG_VERBOSE: bool = False


settings = Settings()


def setup_logging(level=None):
    """Setup logging configuration."""
    if level is None:
        level = settings.LOG_LEVEL

    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )

    # Create logs directory
    os.makedirs(settings.LOG_FILE_PATH, exist_ok=True)
