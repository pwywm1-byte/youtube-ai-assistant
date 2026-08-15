"""Visual assets service using Unsplash and Pexels APIs."""

import logging
import os
import requests
from typing import Dict, Any, List, Optional

from config import settings

logger = logging.getLogger(__name__)

UNSPLASH_BASE = "https://api.unsplash.com"
PEXELS_BASE = "https://api.pexels.com/v1"


class VisualService:
    """Fetch images and stock footage from Unsplash and Pexels."""

    def __init__(self, output_dir: str = "./storage/visuals"):
        """Initialize visual service."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.unsplash_key: Optional[str] = getattr(settings, "UNSPLASH_ACCESS_KEY", None)
        self.pexels_key: Optional[str] = getattr(settings, "PEXELS_API_KEY", None)
        logger.info("Visual service initialized")

    def search_unsplash(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Search Unsplash for images matching a query.

        Returns a list of image dicts with urls and attribution.
        """
        if not self.unsplash_key:
            logger.warning("UNSPLASH_ACCESS_KEY not configured – skipping Unsplash search.")
            return []

        try:
            response = requests.get(
                f"{UNSPLASH_BASE}/search/photos",
                headers={"Authorization": f"Client-ID {self.unsplash_key}"},
                params={"query": query, "per_page": count, "orientation": "landscape"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            results = []
            for photo in data.get("results", []):
                results.append({
                    "id": photo.get("id"),
                    "url": photo["urls"].get("regular"),
                    "download_url": photo["urls"].get("full"),
                    "photographer": photo.get("user", {}).get("name"),
                    "source": "unsplash",
                })
            logger.info(f"Unsplash: found {len(results)} images for '{query}'")
            return results
        except Exception as e:
            logger.error(f"Unsplash search error: {e}")
            return []

    def search_pexels(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Search Pexels for stock photos matching a query."""
        if not self.pexels_key:
            logger.warning("PEXELS_API_KEY not configured – skipping Pexels search.")
            return []

        try:
            response = requests.get(
                f"{PEXELS_BASE}/search",
                headers={"Authorization": self.pexels_key},
                params={"query": query, "per_page": count, "orientation": "landscape"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            results = []
            for photo in data.get("photos", []):
                results.append({
                    "id": photo.get("id"),
                    "url": photo["src"].get("large"),
                    "download_url": photo["src"].get("original"),
                    "photographer": photo.get("photographer"),
                    "source": "pexels",
                })
            logger.info(f"Pexels: found {len(results)} images for '{query}'")
            return results
        except Exception as e:
            logger.error(f"Pexels search error: {e}")
            return []

    def search_pexels_videos(self, query: str, count: int = 3) -> List[Dict[str, Any]]:
        """Search Pexels for stock video clips."""
        if not self.pexels_key:
            logger.warning("PEXELS_API_KEY not configured – skipping Pexels video search.")
            return []

        try:
            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers={"Authorization": self.pexels_key},
                params={"query": query, "per_page": count, "orientation": "landscape"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            results = []
            for video in data.get("videos", []):
                # Pick the HD file if available
                files = video.get("video_files", [])
                hd_files = [f for f in files if f.get("quality") == "hd"]
                video_url = hd_files[0]["link"] if hd_files else (files[0]["link"] if files else None)
                if video_url:
                    results.append({
                        "id": video.get("id"),
                        "url": video_url,
                        "duration": video.get("duration"),
                        "photographer": video.get("user", {}).get("name"),
                        "source": "pexels_video",
                    })
            logger.info(f"Pexels Videos: found {len(results)} clips for '{query}'")
            return results
        except Exception as e:
            logger.error(f"Pexels video search error: {e}")
            return []

    def gather_assets(self, topic: str, count: int = 5) -> Dict[str, Any]:
        """Gather combined visual assets (images + videos) for a topic."""
        images = self.search_unsplash(topic, count) + self.search_pexels(topic, count)
        videos = self.search_pexels_videos(topic, 3)
        return {
            "topic": topic,
            "images": images,
            "videos": videos,
            "total_assets": len(images) + len(videos),
        }
