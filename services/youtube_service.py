"""YouTube API service for video management and publishing."""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    _GOOGLE_LIBS = True
except ImportError:  # pragma: no cover
    _GOOGLE_LIBS = False
    logger.warning("google-api-python-client not installed; YouTube upload disabled")

_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
_TOKEN_FILE = "youtube_token.json"
_CLIENT_SECRETS_FILE = "client_secrets.json"


class YouTubeService:
    """Handle YouTube Data API v3 operations.

    Authentication modes (in priority order):
    1. Refresh token via env vars  ``YOUTUBE_CLIENT_ID``, ``YOUTUBE_CLIENT_SECRET``,
       ``YOUTUBE_REFRESH_TOKEN``.
    2. OAuth 2.0 interactive flow using *client_secrets.json* (local dev only).
    3. No credentials — mock mode (returns placeholder data so the pipeline
       can run without YouTube credentials during development).
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._service = None
        self._mock = False

        if _GOOGLE_LIBS:
            self._service = self._build_service()
        else:
            self._mock = True

        if self._service is None:
            self._mock = True

        mode = "mock" if self._mock else "authenticated"
        logger.info("YouTube Service initialised (%s)", mode)

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _build_service(self):
        """Return an authenticated YouTube API service, or None if not possible."""
        creds = self._creds_from_env()
        if creds is None:
            creds = self._creds_from_token_file()
        if creds is None:
            logger.warning(
                "No YouTube credentials available. "
                "Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN "
                "or provide client_secrets.json for OAuth flow."
            )
            return None
        try:
            return build("youtube", "v3", credentials=creds)
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to build YouTube service: %s", exc)
            return None

    def _creds_from_env(self) -> Optional["Credentials"]:
        """Build credentials from environment refresh token."""
        if not (self._client_id and self._client_secret and self._refresh_token):
            return None
        creds = Credentials(
            token=None,
            refresh_token=self._refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self._client_id,
            client_secret=self._client_secret,
            scopes=_SCOPES,
        )
        try:
            creds.refresh(Request())
            return creds
        except Exception as exc:
            logger.error("Failed to refresh YouTube token from env: %s", exc)
            return None

    def _creds_from_token_file(self) -> Optional["Credentials"]:
        """Load credentials from saved token file."""
        if not os.path.exists(_TOKEN_FILE):
            return None
        try:
            creds = Credentials.from_authorized_user_file(_TOKEN_FILE, _SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._save_token(creds)
            return creds if creds and creds.valid else None
        except Exception as exc:
            logger.warning("Could not load token file: %s", exc)
            return None

    @staticmethod
    def _save_token(creds: "Credentials") -> None:
        with open(_TOKEN_FILE, "w") as fh:
            fh.write(creds.to_json())
        logger.info("YouTube token saved to %s", _TOKEN_FILE)

    def run_oauth_flow(self) -> bool:
        """Run interactive OAuth 2.0 flow (local dev / first-time setup).

        Requires *client_secrets.json* in the project root.
        Saves the resulting token to *youtube_token.json*.
        """
        if not _GOOGLE_LIBS:
            logger.error("google-auth-oauthlib not installed")
            return False
        if not os.path.exists(_CLIENT_SECRETS_FILE):
            logger.error("client_secrets.json not found. Download it from Google Cloud Console.")
            return False
        try:
            flow = InstalledAppFlow.from_client_secrets_file(_CLIENT_SECRETS_FILE, _SCOPES)
            creds = flow.run_local_server(port=0)
            self._save_token(creds)
            self._service = build("youtube", "v3", credentials=creds)
            self._mock = False
            logger.info("OAuth flow completed successfully")
            return True
        except Exception as exc:
            logger.error("OAuth flow failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Video upload
    # ------------------------------------------------------------------

    async def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: List[str],
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "private",
        thumbnail_path: Optional[str] = None,
        is_short: bool = False,
    ) -> Dict[str, Any]:
        """Upload a video file to YouTube.

        Returns a dict with ``success``, ``video_id``, and ``url`` keys.
        When in mock mode the method returns placeholder data so the pipeline
        can run without real credentials.
        """
        if self._mock:
            logger.warning("YouTube mock mode — skipping real upload for: %s", title)
            return {
                "success": True,
                "video_id": "MOCK_VIDEO_ID",
                "url": "https://youtube.com/watch?v=MOCK_VIDEO_ID",
                "used_mock": True,
            }

        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video file not found: {video_path}"}

        if is_short and "#Shorts" not in description:
            description += "\n\n#Shorts"

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:30],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }
        try:
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = self._service.videos().insert(
                part="snippet,status", body=body, media_body=media
            )
            response = None
            while response is None:
                _, response = request.next_chunk()
            video_id = response["id"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            logger.info("Video uploaded: %s -> %s", title, url)

            if thumbnail_path and os.path.exists(thumbnail_path):
                await self.set_thumbnail(video_id, thumbnail_path)

            return {"success": True, "video_id": video_id, "url": url}
        except HttpError as exc:
            logger.error("YouTube upload failed: %s", exc)
            return {"success": False, "error": str(exc)}
        except Exception as exc:
            logger.error("Unexpected error during upload: %s", exc)
            return {"success": False, "error": str(exc)}

    async def set_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """Upload a custom thumbnail for *video_id*."""
        if self._mock:
            return True
        if not os.path.exists(thumbnail_path):
            logger.warning("Thumbnail file not found: %s", thumbnail_path)
            return False
        try:
            self._service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path),
            ).execute()
            logger.info("Thumbnail set for video: %s", video_id)
            return True
        except HttpError as exc:
            logger.error("Failed to set thumbnail: %s", exc)
            return False

    async def publish_video(self, video_id: str) -> bool:
        """Make a previously uploaded (private) video public."""
        if self._mock:
            return True
        try:
            self._service.videos().update(
                part="status",
                body={"id": video_id, "status": {"privacyStatus": "public"}},
            ).execute()
            logger.info("Video published: %s", video_id)
            return True
        except HttpError as exc:
            logger.error("Failed to publish video %s: %s", video_id, exc)
            return False

    async def get_video_stats(self, video_id: str) -> Dict[str, Any]:
        """Fetch statistics for a video."""
        if self._mock:
            return {
                "success": True,
                "stats": {"views": 0, "likes": 0, "comments": 0},
                "used_mock": True,
            }
        try:
            response = self._service.videos().list(part="statistics", id=video_id).execute()
            items = response.get("items", [])
            if not items:
                return {"success": False, "error": "Video not found"}
            stats = items[0].get("statistics", {})
            return {
                "success": True,
                "stats": {
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                },
            }
        except HttpError as exc:
            logger.error("Failed to get video stats: %s", exc)
            return {"success": False, "error": str(exc)}

    async def list_channel_videos(self, channel_id: str, max_results: int = 25) -> Dict[str, Any]:
        """List recent videos from a channel."""
        if self._mock:
            return {"success": True, "videos": [], "used_mock": True}
        try:
            response = (
                self._service.search()
                .list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=max_results,
                    order="date",
                    type="video",
                )
                .execute()
            )
            videos = [
                {
                    "video_id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                }
                for item in response.get("items", [])
            ]
            return {"success": True, "videos": videos}
        except HttpError as exc:
            logger.error("Failed to list channel videos: %s", exc)
            return {"success": False, "error": str(exc)}
