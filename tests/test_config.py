"""Test configuration module."""

from config import settings, setup_logging
import logging


def test_settings_load():
    """Test settings load correctly."""
    assert settings.API_HOST == "0.0.0.0"
    assert settings.API_PORT == 8000
    assert settings.LOG_LEVEL == "INFO"


def test_logging_setup():
    """Test logging setup."""
    setup_logging()
    logger = logging.getLogger("test")
    assert logger is not None


def test_youtube_settings():
    """Test YouTube settings are defined."""
    assert hasattr(settings, "YOUTUBE_CLIENT_ID")
    assert hasattr(settings, "YOUTUBE_CLIENT_SECRET")
    assert hasattr(settings, "YOUTUBE_CHANNEL_ID")


def test_ai_service_settings():
    """Test AI service settings are defined."""
    assert hasattr(settings, "OPENAI_API_KEY")
    assert hasattr(settings, "ANTHROPIC_API_KEY")
    assert hasattr(settings, "ELEVENLABS_API_KEY")
