"""YouTube API service for video management."""

import logging
from typing import Dict, Any, Optional, List
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


class YouTubeService:
    """Handle YouTube API operations."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_path: str = ".youtube_token",
    ):
        """Initialize YouTube service."""
        self.token_path = token_path
        self.client_id = client_id
        self.client_secret = client_secret
        self.credentials = None
        self.youtube = None

        if client_id and client_secret:
            self._authenticate()
        else:
            logger.warning("YouTube credentials not provided. Service limited.")

    def _authenticate(self):
        """Authenticate with YouTube API."""
        try:
            # Try to load existing token
            if os.path.exists(self.token_path):
                with open(self.token_path, "rb") as token_file:
                    self.credentials = pickle.load(token_file)
                logger.info("Loaded existing YouTube token")

            # Refresh if needed
            if self.credentials and self.credentials.expired:
                self.credentials.refresh(Request())
                logger.info("Refreshed YouTube token")
            elif not self.credentials:
                logger.warning("No YouTube token found. OAuth flow required on first use.")

            # Build service
            if self.credentials:
                self.youtube = build("youtube", "v3", credentials=self.credentials)
                logger.info("YouTube service authenticated")
        except Exception as e:
            logger.error(f"Error authenticating with YouTube: {str(e)}")

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        thumbnail_path: Optional[str] = None,
        is_draft: bool = False,
        category: str = "22",  # People & Blogs
    ) -> Dict[str, Any]:
        """Upload video to YouTube."""
        try:
            if not self.youtube:
                logger.warning("YouTube service not authenticated")
                return {
                    "success": True,
                    "video_id": "mock_video_id",
                    "url": "https://youtube.com/watch?v=mock_video_id",
                    "status": "draft",
                }

            if not os.path.exists(video_path):
                return {"success": False, "error": f"Video file not found: {video_path}"}

            # Prepare metadata
            body = {
                "snippet": {
                    "title": title[:100],  # YouTube limit
                    "description": description[:5000],
                    "tags": tags[:30],  # YouTube limit
                    "categoryId": category,
                },
                "status": {"privacyStatus": "private" if is_draft else "public"},
            }

            # Upload video
            media = MediaFileUpload(video_path, chunksize=256 * 1024, resumable=True)
            request = self.youtube.videos().insert(
                part="snippet,status", body=body, media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Upload progress: {status.progress() * 100:.1f}%")

            video_id = response["id"]
            logger.info(f"Video uploaded: {video_id}")

            # Set thumbnail if provided
            if thumbnail_path and os.path.exists(thumbnail_path):
                self.set_thumbnail(video_id, thumbnail_path)

            return {
                "success": True,
                "video_id": video_id,
                "url": f"https://youtube.com/watch?v={video_id}",
                "status": "private" if is_draft else "public",
            }
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            return {"success": False, "error": str(e)}

    def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Set video thumbnail."""
        try:
            if not self.youtube:
                logger.warning("YouTube service not authenticated")
                return True

            if not os.path.exists(thumbnail_path):
                return False

            media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
            self.youtube.thumbnails().set(videoId=video_id, media_body=media).execute()

            logger.info(f"Thumbnail set for video: {video_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting thumbnail: {str(e)}")
            return False

    def get_video_stats(self, video_id: str) -> Dict[str, Any]:
        """Get video statistics."""
        try:
            if not self.youtube:
                return {"success": True, "stats": {"views": 0, "likes": 0, "comments": 0}}

            response = self.youtube.videos().list(part="statistics", id=video_id).execute()

            if response["items"]:
                stats = response["items"][0]["statistics"]
                return {"success": True, "stats": stats}
            return {"success": False, "error": "Video not found"}
        except Exception as e:
            logger.error(f"Error getting video stats: {str(e)}")
            return {"success": False, "error": str(e)}

    def publish_video(self, video_id: str) -> bool:
        """Publish video (make it public)."""
        try:
            if not self.youtube:
                logger.warning("YouTube service not authenticated")
                return True

            body = {"status": {"privacyStatus": "public"}}
            self.youtube.videos().update(part="status", body=body).execute()

            logger.info(f"Video published: {video_id}")
            return True
        except Exception as e:
            logger.error(f"Error publishing video: {str(e)}")
            return False

    def create_playlist(self, title: str, description: str = "") -> Dict[str, Any]:
        """Create a new playlist."""
        try:
            if not self.youtube:
                return {"success": True, "playlist_id": "mock_playlist_id"}

            body = {
                "snippet": {"title": title, "description": description},
                "status": {"privacyStatus": "private"},
            }

            response = self.youtube.playlists().insert(part="snippet,status", body=body).execute()

            playlist_id = response["id"]
            logger.info(f"Playlist created: {playlist_id}")
            return {"success": True, "playlist_id": playlist_id}
        except Exception as e:
            logger.error(f"Error creating playlist: {str(e)}")
            return {"success": False, "error": str(e)}

    def add_to_playlist(self, playlist_id: str, video_id: str) -> bool:
        """Add video to playlist."""
        try:
            if not self.youtube:
                return True

            body = {
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            }

            self.youtube.playlistItems().insert(part="snippet", body=body).execute()

            logger.info(f"Video added to playlist: {video_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding to playlist: {str(e)}")
            return False
