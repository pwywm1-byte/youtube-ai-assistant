"""Content models for database."""

from sqlalchemy import Column, String, Text, Integer, Boolean, JSON, Float
from datetime import datetime
from .base import BaseModel


class ContentTopic(BaseModel):
    """Trending topics discovered by research agent."""

    __tablename__ = "content_topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    trend_score = Column(Float, default=0.0)
    source = Column(String(100))  # youtube, google, reddit, news
    research_data = Column(JSON, nullable=True)
    is_processed = Column(Boolean, default=False)


class GeneratedScript(BaseModel):
    """Generated video scripts."""

    __tablename__ = "generated_scripts"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, index=True)
    title = Column(String(500), nullable=False)
    hook = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    outro = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    video_type = Column(String(50))  # short, long_form
    seo_keywords = Column(JSON, nullable=True)
    seo_tags = Column(JSON, nullable=True)
    thumbnail_suggestions = Column(JSON, nullable=True)


class GeneratedVideo(BaseModel):
    """Generated and published videos."""

    __tablename__ = "generated_videos"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, index=True)
    youtube_video_id = Column(String(100), unique=True, nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    duration = Column(Integer)  # seconds
    status = Column(String(50), default="draft")  # draft, published, processing
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    retention_rate = Column(Float, default=0.0)
    video_type = Column(String(50))  # short, long_form
    publish_time = Column(String(50), nullable=True)


class AnalyticsSnapshot(BaseModel):
    """Video performance analytics."""

    __tablename__ = "analytics_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, index=True)
    youtube_video_id = Column(String(100), index=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    watch_time_hours = Column(Float, default=0.0)
    retention_rate = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)  # Click-through rate
    avg_view_duration = Column(Integer, default=0)  # seconds
