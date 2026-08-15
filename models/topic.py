"""Topic model for database."""

from sqlalchemy import Column, String, Integer, Float, JSON, Boolean
from .base import BaseModel


class Topic(BaseModel):
    """Topic database model."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)
    description = Column(String(1000), nullable=True)
    
    popularity_score = Column(Float, default=0.0)
    searchability_score = Column(Float, default=0.0)
    competition_score = Column(Float, default=0.0)
    monetization_potential = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    sources = Column(JSON, nullable=True)
    
    is_selected = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    videos_created = Column(Integer, default=0)
    
    category = Column(String(100), nullable=True)
    tags = Column(JSON, nullable=True)
    related_topics = Column(JSON, nullable=True)
