"""Pexels video and image service."""

import logging
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)


class PexelsService:
    """Fetch videos and images from Pexels API."""

    def __init__(self, api_key: str):
        """Initialize Pexels service."""
        try:
            import requests
            self.requests = requests
            self.api_key = api_key
            self.base_url = "https://api.pexels.com"
            logger.info("Pexels Service initialized")
        except ImportError:
            logger.warning("requests not available")
            self.requests = None

    def search_videos(
        self,
        query: str,
        count: int = 5,
        download: bool = False,
        output_dir: str = "storage/videos",
    ) -> Dict[str, Any]:
        """Search for videos on Pexels."""
        try:
            if not self.requests or not self.api_key:
                logger.warning("Pexels not configured. Returning mock results.")
                return {
                    "success": True,
                    "videos": [
                        {
                            "id": f"mock_{i}",
                            "url": f"https://www.pexels.com/video/{i}",
                            "description": f"Mock video for {query}",
                        }
                        for i in range(count)
                    ],
                }

            response = self.requests.get(
                f"{self.base_url}/v1/videos/search",
                headers={"Authorization": self.api_key},
                params={"query": query, "per_page": count},
            )

            if response.status_code != 200:
                logger.error(f"Pexels API error: {response.status_code}")
                return {"success": False, "error": f"API error: {response.status_code}"}

            results = response.json().get("videos", [])
            videos = []

            for i, video in enumerate(results):
                video_data = {
                    "id": video["id"],
                    "url": video["url"],
                    "description": query,
                    "duration": video["duration"],
                }

                if video.get("video_files"):
                    # Get the smallest HD file
                    files = sorted(
                        video["video_files"],
                        key=lambda x: x.get("file_size", 0),
                    )
                    if files:
                        video_data["download_url"] = files[0]["link"]

                videos.append(video_data)

            return {"success": True, "videos": videos, "query": query}
        except Exception as e:
            logger.error(f"Error searching videos: {str(e)}")
            return {"success": False, "error": str(e)}

    def search_images(
        self, query: str, count: int = 5
    ) -> Dict[str, Any]:
        """Search for images on Pexels."""
        try:
            if not self.requests or not self.api_key:
                logger.warning("Pexels not configured. Returning mock results.")
                return {
                    "success": True,
                    "images": [
                        {
                            "id": f"mock_{i}",
                            "url": f"https://via.placeholder.com/1080x720?text=Image+{i}",
                            "description": f"Mock image for {query}",
                        }
                        for i in range(count)
                    ],
                }

            response = self.requests.get(
                f"{self.base_url}/v1/search",
                headers={"Authorization": self.api_key},
                params={"query": query, "per_page": count},
            )

            if response.status_code != 200:
                return {"success": False, "error": f"API error: {response.status_code}"}

            results = response.json().get("photos", [])
            images = []

            for result in results:
                images.append(
                    {
                        "id": result["id"],
                        "url": result["src"]["large"],
                        "description": query,
                        "photographer": result["photographer"],
                    }
                )

            return {"success": True, "images": images, "query": query}
        except Exception as e:
            logger.error(f"Error searching images: {str(e)}")
            return {"success": False, "error": str(e)}
