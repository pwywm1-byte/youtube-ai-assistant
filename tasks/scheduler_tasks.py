"""Celery tasks for computing and persisting publish slots."""
from __future__ import annotations

from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import logging

from services.publish_scheduler import get_top_slots
from models.publish import Base, PublishSlot

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set to run scheduler tasks")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@shared_task(bind=True, name="scheduler.compute_publish_slots")
def compute_publish_slots(self):
    """Compute top slots and persist them to DB."""
    logger.info("Starting compute_publish_slots task")
    # ensure tables exist (simple approach)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        slots = get_top_slots(db, limit=10, tz_offset_minutes=int(os.getenv("PUBLISH_TZ_OFFSET_MINUTES", "0")))
        # delete old slots
        db.query(PublishSlot).delete()
        for s in slots:
            db.add(s)
        db.commit()
        logger.info("Persisted %d publish slots", len(slots))
        return {"persisted": len(slots)}
    except Exception as e:
        logger.exception("Error computing publish slots: %s", e)
        db.rollback()
        raise
    finally:
        db.close()
