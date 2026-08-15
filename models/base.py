"""Base model for all database models."""

from datetime import datetime
from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields."""

    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


def init_db(database_url: str) -> sessionmaker:
    """Initialize database engine and create all tables.

    Args:
        database_url: SQLAlchemy-compatible database URL.

    Returns:
        A configured sessionmaker factory.
    """
    engine = create_engine(database_url, echo=False, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return Session
