"""Tasks module for content generation scheduling."""

import logging

from .daily_content_generation import (
    generate_daily_content_task,
    fetch_analytics_task,
    optimize_content_task,
)

logger = logging.getLogger(__name__)


def debug_task():
    """Simple debug/health-check task."""
    logger.info("Debug task executed successfully.")
    return {"success": True, "message": "Debug task OK"}


__all__ = [
    "debug_task",
    "generate_daily_content_task",
    "fetch_analytics_task",
    "optimize_content_task",
]
