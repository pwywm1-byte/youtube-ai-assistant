"""FastAPI router exposing scheduler endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
from datetime import datetime

from models.publish import PublishSlot
from services.publish_scheduler import get_top_slots, recommend_publish_time
from api.deps import get_db

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/top-slots")
def top_slots(limit: int = 5, db: Session = Depends(get_db)):
    slots = get_top_slots(db, limit=limit, tz_offset_minutes=int(os.getenv("PUBLISH_TZ_OFFSET_MINUTES", "0")))
    return [
        {
            "hour_bucket": s.hour_bucket,
            "score": s.score,
            "estimated_views": s.estimated_views,
            "samples": s.samples,
        }
        for s in slots
    ]


@router.get("/recommend")
def recommend(days_ahead: int = 1, db: Session = Depends(get_db)):
    dt = recommend_publish_time(db, days_ahead=days_ahead, tz_offset_minutes=int(os.getenv("PUBLISH_TZ_OFFSET_MINUTES", "0")))
    if not dt:
        raise HTTPException(status_code=404, detail="No recommendation available")
    return {"publish_at_utc": dt.isoformat()}
