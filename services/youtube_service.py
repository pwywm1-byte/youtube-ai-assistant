"""YouTube API service for video management."""

import logging
import os
from typing import Dict, Any, Optional

from config import settings

logger = logging.getLogger(__name__)


def _build_youtube_client():
    """Build an authenticated YouTube API client using OAuth2 credentials."""
    from google.oauth2.credentials import Credentials  # type: ignore
    from googleapiclient.discovery import build  # type: ignore

    creds = Credentials(
        token=None,
        refresh_token=settings.YOUTUBE_REFRESH_TOKEN,
        client_id=settings.YOUTUBE_CLIENT_ID,
        client_secret=settings.YOUTUBE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    return build("youtube", "v3", credentials=creds)


class YouTubeService:
    """Handle YouTube API operations."""

    def __init__(self):
        """Initialize YouTube service."""
        self._client = None
        logger.info("YouTube Service initialized")

    @property
    def client(self):
        """Lazily build and cache the YouTube API client."""
        if self._client is None:
            if not all([
                settings.YOUTUBE_CLIENT_ID,
                settings.YOUTUBE_CLIENT_SECRET,
                settings.YOUTUBE_REFRESH_TOKEN,
            ]):
                raise ValueError(
                    "YouTube OAuth credentials are not fully configured. "
                    "Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN in .env"
                )
            self._client = _build_youtube_client()
        return self._client

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        thumbnail_path: Optional[str] = None,
        is_draft: bool = False,
    ) -> Dict[str, Any]:
        """Upload a video file to YouTube.

        Args:
            video_path: Local path to the video file.
            title: Video title.
            description: Video description.
            tags: List of tag strings.
            thumbnail_path: Optional path to thumbnail image.
            is_draft: If True, upload as private/draft.

        Returns:
            Dict with video_id and url on success.
        """
        try:
            from googleapiclient.http import MediaFileUpload  # type: ignore

            logger.info(f"Uploading video: {title}")
            privacy = "private" if is_draft else "public"
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": "22",  # People & Blogs
                },
                "status": {"privacyStatus": privacy},
            }
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = self.client.videos().insert(
                part="snippet,status", body=body, media_body=media
            )
            response = request.execute()
            video_id = response.get("id")
            logger.info(f"Video uploaded: {video_id}")

            if thumbnail_path and os.path.exists(thumbnail_path):
                await self.set_thumbnail(video_id, thumbnail_path)

            return {
                "success": True,
                "video_id": video_id,
                "url": f"https://youtube.com/watch?v={video_id}",
            }
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            raise

    async def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Set video thumbnail."""
        try:
            from googleapiclient.http import MediaFileUpload  # type: ignore

            logger.info(f"Setting thumbnail for video: {video_id}")
            media = MediaFileUpload(thumbnail_path)
            self.client.thumbnails().set(videoId=video_id, media_body=media).execute()
            return True
        except Exception as e:
            logger.error(f"Error setting thumbnail: {str(e)}")
            raise

    async def publish_video(self, video_id: str) -> bool:
        """Publish a private/draft video (make it public)."""
        try:
            logger.info(f"Publishing video: {video_id}")
            self.client.videos().update(
                part="status",
                body={"id": video_id, "status": {"privacyStatus": "public"}},
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error publishing video: {str(e)}")
            raise
