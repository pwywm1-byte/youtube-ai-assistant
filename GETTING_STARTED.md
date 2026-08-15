## Scheduler and optimal publish settings

This feature adds an adaptive scheduler that computes the best hours to
publish videos to maximize views using historical YouTube Analytics and
channel publish history.

Key files added (branch: feature/optimal-publish-scheduler):

- services/publish_scheduler.py  -- scoring & recommendation logic
- services/youtube_client.py     -- thin wrappers for YouTube Analytics & uploads
- models/publish.py              -- DB models for publish history and slots
- tasks/scheduler_tasks.py       -- Celery task to compute & persist top slots
- api/scheduler.py               -- FastAPI endpoints to inspect recommendations
- api/deps.py                    -- DB dependency helper
- run_content_generation.py      -- integrated to consult scheduler before upload
- tests/test_scheduler.py        -- basic unit test for scoring

Environment variables (important):
- DATABASE_URL (required)
- YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN (for live API)
- PUBLISH_TZ_OFFSET_MINUTES (timezone offset of target audience)
- LAST_VIDEO_FILE (path used by run_content_generation when uploading)

How it works (short):
1. The Celery task `scheduler.compute_publish_slots` reads historical
   publish records (or you can extend it to pull from YouTube Analytics),
   computes per-hour bucket scores and persists top slots to the DB.
2. The content pipeline asks the scheduler for a recommended publish_at
   time. If available, uploads are scheduled (private + publishAt). If
   not, uploads are immediate.

Next steps (recommended):
- Populate publish_history either by importing past video analytics
  (using services/youtube_client.fetch_channel_analytics) or by
  inserting records when uploads finish.
- Configure Celery Beat (or a GitHub Action) to run
  scheduler.compute_publish_slots once per day.
- Add monitoring for upload failures and quota errors.
