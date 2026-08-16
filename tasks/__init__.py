"""Tasks module for Celery background jobs."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def debug_task():
    """Debug task for testing."""
    logger.info("Debug task executed at %s", datetime.utcnow())
    return {"success": True, "timestamp": datetime.utcnow().isoformat()}


__all__ = ["debug_task"]
