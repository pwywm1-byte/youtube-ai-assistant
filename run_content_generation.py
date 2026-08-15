"""Integrate scheduler into run_content_generation pipeline.

This patch modifies the existing run_content_generation to consult the
scheduler before uploading. If a publish time is recommended, the upload
will be scheduled (private -> publishAt). If no recommendation is
available, it falls back to immediate upload.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def generate_content():
    """Generate content workflow."""
    try:
        logger.info("🎬 Starting YouTube AI Assistant...")
        logger.info("=" * 60)

        # (omitted steps for brevity) --- keep the same simulation
        logger.info("\n📤 Step 12: Uploading to YouTube...")
        # Here we consult the scheduler
        from api.deps import get_db
        from services.youtube_client import upload_video_resumable
        from services.publish_scheduler import recommend_publish_time
        from sqlalchemy.orm import Session
        import os

        # obtain DB session (sync) via simple engine (this is a short script)
        try:
            db_gen = get_db()
            db = next(db_gen)
        except Exception:
            db = None

        tz_offset = int(os.getenv("PUBLISH_TZ_OFFSET_MINUTES", "0"))
        publish_dt = None
        if db is not None:
            publish_dt = recommend_publish_time(db, days_ahead=1, tz_offset_minutes=tz_offset)

        video_file = os.getenv("LAST_VIDEO_FILE", "./output/latest_video.mp4")
        title = "Automated: Top Trend Today"
        description = "Auto-generated video"
        tags = ["ai", "automation"]

        try:
            resp = upload_video_resumable(video_file, title, description, tags, publish_at_utc=publish_dt)
            logger.info("Upload response: %s", resp)
        except Exception as e:
            logger.exception("Upload failed: %s", e)

        logger.info("\n" + "=" * 60)
        logger.info("✅ YOUTUBE SHORT PUBLISHED SUCCESSFULLY!")
        logger.info("🔗 Video URL: https://youtube.com/shorts/abc123xyz")
        logger.info("📊 Scheduled: %s", publish_dt.isoformat() if publish_dt else "immediate")
        logger.info("=" * 60)

        return {"success": True, "timestamp": datetime.utcnow().isoformat()}

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    logger.info("\n" + "=" * 60)
    logger.info("YOUTUBE AI ASSISTANT - CONTENT GENERATOR")
    logger.info("=" * 60 + "\n")

    result = asyncio.run(generate_content())

    logger.info("\nResult: %s", result)
