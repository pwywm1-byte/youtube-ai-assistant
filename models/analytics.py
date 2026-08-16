"""Analytics model for database."""

from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from datetime import datetime
from .base import BaseModel


class Analytics(BaseModel):
    """Analytics database model."""

    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True)
    video_id = Column(String(255), nullable=False)

    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    watch_time = Column(Float, default=0.0)
    retention_rate = Column(Float, default=0.0)
    ctr = Column(Float, default=0.0)

    like_rate = Column(Float, default=0.0)
    comment_rate = Column(Float, default=0.0)
    share_rate = Column(Float, default=0.0)

    audience_data = Column(JSON, nullable=True)
    traffic_sources = Column(JSON, nullable=True)
    device_types = Column(JSON, nullable=True)

    performance_score = Column(Float, default=0.0)
    revenue_estimate = Column(Float, default=0.0)

    snapshot_time = Column(DateTime, default=datetime.utcnow)
