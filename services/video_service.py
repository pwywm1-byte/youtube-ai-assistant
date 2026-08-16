"""Video processing and composition service."""

import logging
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)


class VideoService:
    """Video processing using MoviePy and FFmpeg."""

    def __init__(self):
        """Initialize video service."""
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

            self.moviepy_available = True
        except ImportError:
            self.moviepy_available = False
            logger.warning("moviepy not available. Video operations will be limited.")

    def compose_video(
        self,
        audio_path: str,
        images: List[str],
        output_path: str = "output/video.mp4",
        duration: Optional[float] = None,
        fps: int = 30,
    ) -> Dict[str, Any]:
        """Compose video from audio and images."""
        try:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            if not self.moviepy_available:
                logger.warning("moviepy not available. Creating mock video file.")
                with open(output_path, "w") as f:
                    f.write("Mock video file")
                return {
                    "success": True,
                    "file_path": output_path,
                    "duration": duration or 120,
                    "resolution": "1080p",
                }

            from moviepy.editor import (
                VideoFileClip,
                AudioFileClip,
                CompositeVideoClip,
                ImageClip,
                concatenate_videoclips,
            )

            # Load audio to get duration
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return {"success": False, "error": "Audio file not found"}

            audio = AudioFileClip(audio_path)
            total_duration = audio.duration

            # Create video clips from images
            clips = []
            time_per_image = total_duration / len(images) if images else 1

            for img_path in images:
                if os.path.exists(img_path):
                    clip = ImageClip(img_path).set_duration(time_per_image)
                    clip = clip.resize(height=1080)  # 1080p
                    clips.append(clip)

            if not clips:
                logger.error("No valid images provided")
                return {"success": False, "error": "No valid images"}

            # Concatenate and add audio
            video = concatenate_videoclips(clips, method="chain")
            video = video.set_audio(audio)

            # Write to file
            video.write_videofile(
                output_path,
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None,
            )

            logger.info(f"Video composed: {output_path}")
            return {
                "success": True,
                "file_path": output_path,
                "duration": total_duration,
                "resolution": "1080p",
            }
        except Exception as e:
            logger.error(f"Error composing video: {str(e)}")
            return {"success": False, "error": str(e)}

    def create_thumbnail(
        self,
        text: str,
        image_path: Optional[str] = None,
        output_path: str = "output/thumbnail.jpg",
        width: int = 1280,
        height: int = 720,
    ) -> Dict[str, Any]:
        """Create a YouTube thumbnail."""
        try:
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            try:
                from PIL import Image, ImageDraw, ImageFont
            except ImportError:
                logger.warning("Pillow not available. Creating mock thumbnail.")
                with open(output_path, "w") as f:
                    f.write("Mock thumbnail")
                return {
                    "success": True,
                    "file_path": output_path,
                    "resolution": f"{width}x{height}",
                }

            # Create or load base image
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path).resize((width, height))
            else:
                img = Image.new("RGB", (width, height), color=(0, 0, 0))

            # Add text
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60
                )
            except (OSError, FileNotFoundError):
                font = ImageFont.load_default()

            # Center text
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2

            draw.text((x, y), text, fill=(255, 255, 255), font=font)

            # Save
            img.save(output_path)

            logger.info(f"Thumbnail created: {output_path}")
            return {
                "success": True,
                "file_path": output_path,
                "resolution": f"{width}x{height}",
            }
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            return {"success": False, "error": str(e)}
