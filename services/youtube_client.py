"""YouTube client helpers: fetch analytics and perform uploads.

This module provides lightweight wrappers around google-api-python-client.
It intentionally keeps interactions isolated so the rest of the codebase
can be tested without making live API calls.

NOTE: You must set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET and
YOUTUBE_REFRESH_TOKEN in env for authenticated calls.
"""
from __future__ import annotations

import os
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_ANALYTICS_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_VERSION = "v2"


def _get_credentials():
    refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
    client_id = os.getenv("YOUTUBE_CLIENT_ID")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
    if not (refresh_token and client_id and client_secret):
        raise RuntimeError("YouTube OAuth credentials are not set in environment")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/yt-analytics.readonly",
            "https://www.googleapis.com/auth/youtube.readonly",
        ],
    )
    # refresh to obtain access token
    creds.refresh(Request())
    return creds


def fetch_channel_analytics(start_date: str, end_date: str, metrics: str = "views,averageViewDuration,impressions") -> Dict[str, Any]:
    """Pull analytics for the authenticated channel between dates (YYYY-MM-DD).

    Returns the raw analytics response. Caller should parse rows.
    """
    creds = _get_credentials()
    analytics = build(YOUTUBE_ANALYTICS_SERVICE_NAME, YOUTUBE_ANALYTICS_VERSION, credentials=creds)

    response = analytics.reports().query(
        ids="channel==MINE",
        startDate=start_date,
        endDate=end_date,
        metrics=metrics,
        dimensions="day",
    ).execute()
    return response


def upload_video_resumable(video_file_path: str, title: str, description: str, tags: list[str], publish_at_utc: datetime | None = None) -> Dict[str, Any]:
    """Upload using resumable upload. If publish_at_utc is provided, video is scheduled.

    Returns API response dict.
    """
    creds = _get_credentials()
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "private" if publish_at_utc else "public",
        },
    }

    if publish_at_utc:
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_at_utc.isoformat("T") + "Z"

    media = MediaFileUpload(video_file_path, chunksize=1024 * 1024, resumable=True)
    request = youtube.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    response = None
    error = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                logger.info("Upload progress: %s%%", int(status.progress() * 100))
        except Exception as e:
            error = e
            logger.exception("Error during upload chunk: %s", e)
            raise

    return response
