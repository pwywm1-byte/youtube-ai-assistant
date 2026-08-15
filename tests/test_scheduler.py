"""Unit tests for publish scheduler scoring logic."""
from datetime import datetime, timedelta

from services.publish_scheduler import compute_slot_scores
from models.publish import PublishHistory


def test_compute_slot_scores_basic():
    now = datetime.utcnow()
    histories = []
    # create sample publishes at different hours
    for i in range(10):
        ph = PublishHistory()
        ph.publish_at = now - timedelta(days=i)
        ph.views = 100 + i * 10
        ph.watch_time = 50 + i
        ph.impressions = 500 + i * 20
        histories.append(ph)

    scores = compute_slot_scores(histories, tz_offset_minutes=0)
    assert isinstance(scores, dict)
    # expect some buckets present
    assert len(scores) > 0
