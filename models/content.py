"""Content models for database."""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from datetime import datetime
from .base import BaseModel


class Topic(BaseModel):
    """Topic model."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    score = Column(Float, default=0.0)
    category = Column(String(100))
    source = Column(String(50))
    published = Column(Integer, default=0)


class Script(BaseModel):
    """Script model."""

    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True)
    topic = Column(String(255), nullable=False)
    video_type = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    hook = Column(Text)
    content = Column(Text, nullable=False)
    outro = Column(Text)
    word_count = Column(Integer, default=0)
    seo_score = Column(Float, default=0.0)
    content_metadata = Column(JSON)


class Video(BaseModel):
    """Video model."""

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    topic = Column(String(255), nullable=False)
    video_type = Column(String(20), nullable=False)
    script_id = Column(Integer)
    file_path = Column(String(500))
    thumbnail_path = Column(String(500))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    duration = Column(Integer)
    resolution = Column(String(20))
    youtube_id = Column(String(50))
    youtube_url = Column(String(500))
    status = Column(String(20), default="draft")
    published_at = Column(DateTime)


class Metadata(BaseModel):
    """Video metadata model."""

    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    tags = Column(JSON)
    keywords = Column(JSON)
    seo_score = Column(Float, default=0.0)
    category = Column(String(100))


class Analytics(BaseModel):
    """Video analytics model."""

    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True)
    video_id = Column(Integer)
    youtube_id = Column(String(50))
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    watch_time = Column(Integer, default=0)
    retention_rate = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)


class Credential(BaseModel):
    """API credentials model."""

    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True)
    service = Column(String(50), nullable=False)
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Integer, default=1)
