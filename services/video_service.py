"""Video composition service using MoviePy / FFmpeg."""

import logging
import os
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class VideoService:
    """Compose video from audio and visual assets using MoviePy."""

    def __init__(self, output_dir: str = "./storage/videos"):
        """Initialize video service."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info("Video service initialized (MoviePy/FFmpeg)")

    def compose_video(
        self,
        audio_path: str,
        image_paths: Optional[List[str]] = None,
        output_filename: str = "output_video.mp4",
        resolution: str = "1920x1080",
    ) -> Dict[str, Any]:
        """Compose a video from an audio track and images using MoviePy.

        Args:
            audio_path: Path to the narration audio file.
            image_paths: List of image file paths to use as slides.
            output_filename: Output video filename.
            resolution: Target resolution string (WxH).

        Returns:
            Dict with file_path, duration, resolution, and format.
        """
        try:
            from moviepy.editor import (  # type: ignore
                AudioFileClip,
                ImageClip,
                concatenate_videoclips,
                ColorClip,
            )
        except ImportError:
            raise ImportError("moviepy is not installed. Run: pip install moviepy")

        output_path = os.path.join(self.output_dir, output_filename)
        width, height = (int(d) for d in resolution.split("x"))

        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        if image_paths:
            # Split audio duration evenly across images
            per_image = duration / len(image_paths)
            clips = []
            for img in image_paths:
                try:
                    clip = ImageClip(img).set_duration(per_image).resize((width, height))
                    clips.append(clip)
                except Exception as img_err:
                    logger.warning(f"Could not load image {img}: {img_err}")

            if clips:
                video_clip = concatenate_videoclips(clips, method="compose")
            else:
                video_clip = ColorClip(size=(width, height), color=(0, 0, 0), duration=duration)
        else:
            video_clip = ColorClip(size=(width, height), color=(0, 0, 0), duration=duration)

        final = video_clip.set_audio(audio_clip)
        final.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )

        logger.info(f"Video composed: {output_path}")
        return {
            "file_path": output_path,
            "duration": duration,
            "resolution": resolution,
            "bitrate": "8000k",
            "format": "mp4",
        }

    def create_thumbnail(
        self,
        image_path: str,
        output_filename: str = "thumbnail.jpg",
        size: tuple = (1280, 720),
    ) -> Dict[str, Any]:
        """Resize/crop an image to YouTube thumbnail dimensions.

        Args:
            image_path: Source image path.
            output_filename: Output thumbnail filename.
            size: (width, height) tuple.

        Returns:
            Dict with file_path and resolution.
        """
        try:
            from PIL import Image  # type: ignore
        except ImportError:
            raise ImportError("Pillow is not installed. Run: pip install Pillow")

        output_path = os.path.join(self.output_dir, output_filename)
        img = Image.open(image_path)
        img = img.convert("RGB")
        img = img.resize(size, Image.LANCZOS)
        img.save(output_path, "JPEG", quality=90)

        logger.info(f"Thumbnail created: {output_path}")
        return {
            "file_path": output_path,
            "resolution": f"{size[0]}x{size[1]}",
            "format": "jpg",
        }
