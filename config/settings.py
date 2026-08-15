"""Application settings."""

import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = False
    API_WORKERS: int = 4
    SECRET_KEY: str = "change-this-in-production"

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/youtube_ai"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # YouTube
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_CHANNEL_ID: Optional[str] = None
    YOUTUBE_REFRESH_TOKEN: Optional[str] = None
    YOUTUBE_API_SERVICE_NAME: str = "youtube"
    YOUTUBE_API_VERSION: str = "v3"

    # Google Cloud
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_OAUTH_CLIENT_SECRETS_FILE: Optional[str] = None
    GOOGLE_OAUTH_TOKEN_FILE: str = "token.json"
    GOOGLE_SERVICE_ACCOUNT_FILE: Optional[str] = None
    GOOGLE_OAUTH_SCOPES: str = (
        "https://www.googleapis.com/auth/youtube.upload,"
        "https://www.googleapis.com/auth/youtube.readonly,"
        "https://www.googleapis.com/auth/youtube"
    )

    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: Optional[str] = None
    ELEVENLABS_MODEL_ID: str = "eleven_multilingual_v2"

    # Video
    VIDEO_QUALITY: str = "1080p"
    VIDEO_BITRATE: str = "8000k"
    AUDIO_BITRATE: str = "192k"

    # Publishing
    PUBLISH_SHORT_TIME: str = "09:00"
    PUBLISH_LONGFORM_TIME: str = "18:00"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "./logs"

    # Development
    DEVELOPMENT_MODE: bool = False
    DEBUG_VERBOSE: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


def setup_logging(level=None):
    """Setup logging configuration."""
    if level is None:
        level = settings.LOG_LEVEL

    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )

    # Create logs directory
    os.makedirs(settings.LOG_FILE_PATH, exist_ok=True)
