"""Test database models."""

from models import Topic, Script, Video, Metadata, Analytics, Credential
from models.base import BaseModel


def test_topic_model():
    """Test Topic model can be instantiated."""
    assert Topic.__tablename__ == "topics"


def test_script_model():
    """Test Script model can be instantiated."""
    assert Script.__tablename__ == "scripts"


def test_video_model():
    """Test Video model can be instantiated."""
    assert Video.__tablename__ == "videos"


def test_metadata_model():
    """Test Metadata model can be instantiated."""
    assert Metadata.__tablename__ == "metadata"


def test_analytics_model():
    """Test Analytics model can be instantiated."""
    assert Analytics.__tablename__ == "analytics"


def test_credential_model():
    """Test Credential model can be instantiated."""
    assert Credential.__tablename__ == "credentials"
