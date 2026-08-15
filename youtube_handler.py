"""YouTube Data API v3 handler."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from google_auth import GoogleAuthManager


class YouTubeHandler:
    """Client wrapper around YouTube Data API v3."""

    def __init__(self, credentials: Any = None) -> None:
        self.channel_id = os.getenv("YOUTUBE_CHANNEL_ID")
        self.api_service_name = os.getenv("YOUTUBE_API_SERVICE_NAME", "youtube")
        self.api_version = os.getenv("YOUTUBE_API_VERSION", "v3")
        self._credentials = credentials
        self._service = None

    def _get_service(self):
        from googleapiclient.discovery import build

        if self._service is None:
            credentials = self._credentials or GoogleAuthManager().get_oauth_credentials()
            self._service = build(self.api_service_name, self.api_version, credentials=credentials)
        return self._service

    @staticmethod
    def _channel_filters(channel_id: str) -> Dict[str, str]:
        return {"forHandle": channel_id} if channel_id.startswith("@") else {"id": channel_id}

    def get_channel_info(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """Get channel metadata for configured channel ID or a provided one."""
        target_channel = channel_id or self.channel_id
        if not target_channel:
            raise ValueError("YOUTUBE_CHANNEL_ID is not set.")

        service = self._get_service()
        request = service.channels().list(
            part="snippet,statistics,contentDetails",
            **self._channel_filters(target_channel),
        )
        response = request.execute()
        items = response.get("items", [])
        if not items:
            raise ValueError(f"No channel found for: {target_channel}")
        return items[0]

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        privacy_status: str = "private",
        category_id: str = "22",
    ) -> Dict[str, Any]:
        """Upload a video to YouTube."""
        from googleapiclient.http import MediaFileUpload

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file does not exist: {video_path}")

        service = self._get_service()
        request = service.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags or [],
                    "categoryId": category_id,
                },
                "status": {"privacyStatus": privacy_status},
            },
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
        )
        return request.execute()

    def create_playlist(
        self, title: str, description: str = "", privacy_status: str = "private"
    ) -> Dict[str, Any]:
        """Create a YouTube playlist."""
        service = self._get_service()
        request = service.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {"title": title, "description": description},
                "status": {"privacyStatus": privacy_status},
            },
        )
        return request.execute()

    def list_playlists(self, channel_id: Optional[str] = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """List playlists for a channel."""
        if max_results < 1 or max_results > 50:
            raise ValueError("max_results must be between 1 and 50.")

        target_channel = channel_id or self.channel_id
        if not target_channel:
            raise ValueError("YOUTUBE_CHANNEL_ID is not set.")

        if target_channel.startswith("@"):
            channel_info = self.get_channel_info(target_channel)
            target_channel = channel_info.get("id")
            if not target_channel:
                raise ValueError("Could not resolve channel handle to channel ID.")

        service = self._get_service()
        request = service.playlists().list(
            part="snippet,contentDetails",
            channelId=target_channel,
            maxResults=max_results,
        )
        response = request.execute()
        return response.get("items", [])

    def add_video_to_playlist(self, playlist_id: str, video_id: str) -> Dict[str, Any]:
        """Add a video to an existing playlist."""
        service = self._get_service()
        request = service.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        )
        return request.execute()
