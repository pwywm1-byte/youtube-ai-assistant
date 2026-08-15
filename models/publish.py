"""SQLAlchemy models for publish scheduler and history."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PublishHistory(Base):
    __tablename__ = "publish_history"

    id = Column(Integer, primary_key=True)
    video_id = Column(String(64), nullable=True)  # YouTube video id
    publish_at = Column(DateTime, nullable=True)  # UTC datetime when published
    views = Column(BigInteger, nullable=True)
    watch_time = Column(Float, nullable=True)  # in minutes
    impressions = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PublishSlot(Base):
    __tablename__ = "publish_slots"

    id = Column(Integer, primary_key=True)
    hour_bucket = Column(Integer, nullable=False)  # 0..23 (start hour for the bucket)
    score = Column(Float, nullable=False)
    estimated_views = Column(Float, nullable=True)
    samples = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
