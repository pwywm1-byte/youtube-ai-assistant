"""Unsplash image service for stock photos."""

import logging
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)


class UnsplashService:
    """Fetch images from Unsplash API."""

    def __init__(self, access_key: str):
        """Initialize Unsplash service."""
        try:
            import requests

            self.requests = requests
            self.access_key = access_key
            self.base_url = "https://api.unsplash.com"
            logger.info("Unsplash Service initialized")
        except ImportError:
            logger.warning("requests not available")
            self.requests = None

    def search_images(
        self,
        query: str,
        count: int = 5,
        download: bool = False,
        output_dir: str = "storage/images",
    ) -> Dict[str, Any]:
        """Search and optionally download images from Unsplash."""
        try:
            if not self.requests or not self.access_key:
                logger.warning("Unsplash not configured. Returning mock results.")
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

            # Search on Unsplash
            response = self.requests.get(
                f"{self.base_url}/search/photos",
                headers={"Authorization": f"Client-ID {self.access_key}"},
                params={"query": query, "per_page": count, "orientation": "landscape"},
            )

            if response.status_code != 200:
                logger.error(f"Unsplash API error: {response.status_code}")
                return {"success": False, "error": f"API error: {response.status_code}"}

            results = response.json().get("results", [])
            images = []

            for i, result in enumerate(results):
                image_data = {
                    "id": result["id"],
                    "url": result["urls"]["regular"],
                    "description": result.get("description", query),
                    "photographer": result["user"]["name"],
                }

                # Download if requested
                if download:
                    os.makedirs(output_dir, exist_ok=True)
                    file_path = os.path.join(output_dir, f"unsplash_{i}.jpg")
                    img_response = self.requests.get(result["urls"]["regular"])
                    if img_response.status_code == 200:
                        with open(file_path, "wb") as f:
                            f.write(img_response.content)
                        image_data["local_path"] = file_path

                images.append(image_data)

            return {"success": True, "images": images, "query": query}
        except Exception as e:
            logger.error(f"Error searching images: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_trending(self, count: int = 10) -> Dict[str, Any]:
        """Get trending images."""
        return self.search_images("trending", count=count)
