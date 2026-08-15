"""Video model for database."""

from sqlalchemy import Column, String, Integer, Float, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Video(BaseModel):
    """Video database model."""

    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    youtube_id = Column(String(255), unique=True, nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    topic = Column(String(255), nullable=False)
    video_type = Column(String(50), nullable=False)  # 'short' or 'long_form'
    
    # File paths
    video_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    audio_path = Column(String(500), nullable=True)
    
    # Metadata
    duration = Column(Integer, nullable=True)  # in seconds
    quality = Column(String(50), default="1080p")
    tags = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(50), default="draft")  # draft, processing, ready, published
    is_published = Column(Boolean, default=False)
    publish_time = Column(String(255), nullable=True)
    
    # Analytics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    watch_time = Column(Float, default=0.0)
    retention_rate = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)  # Click-through rate
    
    # Quality scores
    quality_score = Column(Float, nullable=True)
    seo_score = Column(Float, nullable=True)
    performance_score = Column(Float, nullable=True)
    
    # Additional data
    metadata = Column(JSON, nullable=True)
