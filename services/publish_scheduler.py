"""Publish scheduler service

Provides functions to compute optimal publish times based on historical
publish history stored in the DB and optional YouTube Analytics pulls.

This is a conservative, interpretable implementation:
- Pulls historical data (views, watchTime, impressions) from DB or YouTube Analytics
- Buckets by local hour (0-23) using configured timezone
- Applies time-decay weighting and Bayesian smoothing to compute scores
- Exposes `get_top_slots` and `recommend_publish_time` APIs

The code contains placeholders for Analytics API access; if you provide
YOUTUBE credentials and enable the analytics fetch, the service will
pull fresh data; otherwise it will rely on DB records (useful for
private testing or when you upload old videos first).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

import math
import logging
import os

from sqlalchemy.orm import Session

from models.publish import PublishHistory, PublishSlot

logger = logging.getLogger(__name__)

# Tunable parameters
DECAY_HALF_LIFE_DAYS = int(os.getenv("SCHEDULER_DECAY_HALF_LIFE_DAYS", "30"))
SLOT_BUCKET_HOURS = int(os.getenv("SLOT_BUCKET_HOURS", "1"))  # bucket size in hours
MIN_SAMPLES_PER_SLOT = int(os.getenv("MIN_SAMPLES_PER_SLOT", "5"))


def time_decay_weight(days_old: float) -> float:
    """Exponential decay weight based on days old."""
    # weight = 0.5 ** (days_old / half_life)
    if DECAY_HALF_LIFE_DAYS <= 0:
        return 1.0
    return 0.5 ** (days_old / DECAY_HALF_LIFE_DAYS)


def bucket_hour(dt: datetime, bucket_size_hours: int = SLOT_BUCKET_HOURS) -> int:
    """Return bucket index 0..(24/bucket_size_hours - 1) for a datetime."""
    return (dt.hour // bucket_size_hours) * bucket_size_hours


def bayesian_score(mean: float, count: int, global_mean: float, prior_count: float = 10.0) -> float:
    """Simple Bayesian smoothing: (mean * count + global_mean * prior) / (count + prior)"""
    if count <= 0:
        return global_mean
    return (mean * count + global_mean * prior_count) / (count + prior_count)


def compute_slot_scores(histories: List[PublishHistory], tz_offset_minutes: int = 0, bucket_size_hours: int = SLOT_BUCKET_HOURS) -> Dict[int, Dict]:
    """Compute scores per hour slot.

    Returns a dict keyed by bucket hour with aggregated stats and score.
    """
    now = datetime.utcnow()
    slots = defaultdict(lambda: {"views_w": 0.0, "watchtime_w": 0.0, "impressions_w": 0.0, "count": 0})

    # aggregate weighted metrics per slot
    total_views_w = 0.0
    total_watchtime_w = 0.0
    total_count = 0

    for h in histories:
        # convert stored publish_at (assumed UTC) to target local hour using tz_offset_minutes
        if h.publish_at is None:
            continue
        local_dt = h.publish_at + timedelta(minutes=tz_offset_minutes)
        bucket = bucket_hour(local_dt, bucket_size_hours)

        days_old = max(0.0, (now - h.publish_at).total_seconds() / 86400.0)
        w = time_decay_weight(days_old)

        slots[bucket]["views_w"] += (h.views or 0) * w
        slots[bucket]["watchtime_w"] += (h.watch_time or 0) * w
        slots[bucket]["impressions_w"] += (h.impressions or 0) * w
        slots[bucket]["count"] += 1

        total_views_w += (h.views or 0) * w
        total_watchtime_w += (h.watch_time or 0) * w
        total_count += 1

    # compute global means
    global_mean_views = total_views_w / total_count if total_count > 0 else 0.0

    results = {}
    for bucket, data in slots.items():
        count = data["count"]
        mean_views = data["views_w"] / max(1, count)
        # Bayesian smoothing
        score_views = bayesian_score(mean_views, count, global_mean_views, prior_count=10.0)

        # combine other signals (watchtime, impressions) as multipliers
        watchtime_factor = 1.0
        if data["watchtime_w"] > 0:
            watchtime_factor = (data["watchtime_w"] / max(1, data["views_w"])) if data["views_w"] > 0 else 1.0

        impressions_factor = 1.0
        if data["impressions_w"] > 0:
            impressions_factor = data["impressions_w"] / max(1, data["views_w"]) if data["views_w"] > 0 else 1.0

        # final score is views-based score times small adjustments
        score = score_views * (0.6 + 0.3 * watchtime_factor + 0.1 * impressions_factor)

        results[bucket] = {
            "bucket": bucket,
            "count": count,
            "mean_views": mean_views,
            "score": score,
            "views_w": data["views_w"],
            "watchtime_w": data["watchtime_w"],
            "impressions_w": data["impressions_w"],
        }

    return results


def get_top_slots(db: Session, limit: int = 5, tz_offset_minutes: int = 0) -> List[PublishSlot]:
    """Read historical publishes from DB, compute slot scores, and persist top slots.

    Returns a list of PublishSlot objects (not yet committed by caller).
    """
    histories = db.query(PublishHistory).order_by(PublishHistory.publish_at.desc()).all()
    scores = compute_slot_scores(histories, tz_offset_minutes)

    # sort by score descending
    sorted_slots = sorted(scores.values(), key=lambda s: s.get("score", 0.0), reverse=True)

    slots = []
    for s in sorted_slots[:limit]:
        slot = PublishSlot(
            hour_bucket=s["bucket"],
            score=float(s["score"]),
            estimated_views=float(s["mean_views"]),
            samples=int(s["count"]),
        )
        slots.append(slot)

    return slots


def recommend_publish_time(db: Session, days_ahead: int = 1, tz_offset_minutes: int = 0) -> Optional[datetime]:
    """Recommend a concrete publish datetime for a video.

    Picks the top slot for the target day (days_ahead from now) and returns
    a datetime with that hour in the local timezone offset.
    """
    top = get_top_slots(db, limit=1, tz_offset_minutes=tz_offset_minutes)
    if not top:
        return None

    chosen = top[0]
    now = datetime.utcnow()
    target_local = (now + timedelta(days=days_ahead)) + timedelta(minutes=tz_offset_minutes)
    # set hour to bucket (hour_bucket is a start hour)
    publish_local = target_local.replace(hour=chosen.hour_bucket, minute=0, second=0, microsecond=0)

    # convert back to UTC
    publish_utc = publish_local - timedelta(minutes=tz_offset_minutes)
    return publish_utc
