"""Tasks module for background jobs."""

import logging

logger = logging.getLogger(__name__)


async def debug_task():
    """Debug task for testing."""
    logger.info("Debug task executed")
    return {"status": "success"}
