"""Tests for services."""

import pytest
from services.video_service import VideoService
from services.unsplash_service import UnsplashService
from services.pexels_service import PexelsService


def test_video_service_init():
    """Test video service initialization."""
    service = VideoService()
    assert service is not None


def test_thumbnail_creation(tmp_path):
    """Test thumbnail creation."""
    service = VideoService()
    output_path = str(tmp_path / "test_thumbnail.jpg")
    result = service.create_thumbnail(
        text="Test Video",
        output_path=output_path
    )
    assert result["success"]
    assert "file_path" in result


def test_unsplash_service_init():
    """Test Unsplash service initialization."""
    service = UnsplashService("test_key")
    assert service is not None


def test_pexels_service_init():
    """Test Pexels service initialization."""
    service = PexelsService("test_key")
    assert service is not None
