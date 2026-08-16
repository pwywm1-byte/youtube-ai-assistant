"""ElevenLabs text-to-speech service."""

import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Text-to-speech using ElevenLabs API."""

    def __init__(self, api_key: str):
        """Initialize ElevenLabs service."""
        try:
            from elevenlabs import ElevenLabs

            self.client = ElevenLabs(api_key=api_key)
            logger.info("ElevenLabs Service initialized")
        except ImportError:
            logger.warning("elevenlabs package not installed. Using mock service.")
            self.client = None

    def text_to_speech(
        self,
        text: str,
        voice_id: str = "21m00Tcm4TlvDq8ikWAM",  # Rachel - professional female
        output_path: str = "output/audio.mp3",
    ) -> Dict[str, Any]:
        """Convert text to speech."""
        try:
            if not self.client:
                logger.warning("ElevenLabs client not available. Using mock audio.")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w") as f:
                    f.write("Mock audio file")
                return {
                    "success": True,
                    "file_path": output_path,
                    "duration": len(text.split()) * 0.6,  # Rough estimate
                    "voice_id": voice_id,
                }

            # Create output directory
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            # Generate speech
            audio = self.client.generate(
                text=text, voice_id=voice_id, model="eleven_monolingual_v1"
            )

            # Save to file
            with open(output_path, "wb") as f:
                f.write(audio)

            logger.info(f"Audio generated: {output_path}")
            return {
                "success": True,
                "file_path": output_path,
                "duration": len(text.split()) * 0.6,  # Rough estimate
                "voice_id": voice_id,
            }
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices."""
        try:
            if not self.client:
                return {
                    "success": True,
                    "voices": [
                        {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel"},
                        {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella"},
                        {"id": "MF3mGyEYCHltNiQApNHZ", "name": "Elli"},
                    ],
                }

            voices = self.client.voices.get_all()
            return {
                "success": True,
                "voices": [{"id": v.voice_id, "name": v.name} for v in voices],
            }
        except Exception as e:
            logger.error(f"Error getting voices: {str(e)}")
            return {"success": False, "error": str(e)}
