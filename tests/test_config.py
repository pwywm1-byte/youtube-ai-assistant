"""Tests for configuration."""

import pytest
from config.settings import settings


def test_settings_load():
    """Test that settings load correctly."""
    assert settings is not None
    assert settings.API_HOST == "0.0.0.0"
    assert settings.API_PORT == 8000


def test_settings_defaults():
    """Test default settings."""
    assert settings.LOG_LEVEL == "INFO"
    assert settings.DEVELOPMENT_MODE == False
    assert settings.VIDEO_QUALITY == "1080p"
