"""Base model for all database models."""

from datetime import datetime
from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Optional
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields."""

    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def init_db(database_url: str, echo: bool = False):
    """Initialize database and return sessionmaker."""
    engine = create_engine(database_url, echo=echo, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    logger.info(f"Database initialized: {database_url}")
    return sessionmaker(bind=engine)
