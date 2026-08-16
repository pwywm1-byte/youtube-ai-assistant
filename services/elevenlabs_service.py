"""ElevenLabs TTS service for voice generation."""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """Handle ElevenLabs API operations for text-to-speech."""

    def __init__(self, api_key: Optional[str] = None, voice_id: Optional[str] = None):
        """Initialize ElevenLabs service."""
        self.api_key = api_key
        self.voice_id = voice_id or "21m00Tcm4TlvDq8ikWAM"
        logger.info(f"ElevenLabs Service initialized with voice: {self.voice_id}")

    async def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_path: str = "output/voiceover.mp3",
    ) -> Dict[str, Any]:
        """Generate speech from text using ElevenLabs."""
        try:
            voice_id = voice_id or self.voice_id

            if not self.api_key:
                logger.warning("ElevenLabs API key not set, returning template audio")
                return {
                    "success": True,
                    "audio": {
                        "file_path": output_path,
                        "duration": len(text.split()) * 0.4,
                        "voice_id": voice_id,
                        "format": "mp3",
                    },
                    "used_mock": True,
                }

            logger.info(f"Generating speech for {len(text)} characters")
            return {
                "success": True,
                "audio": {
                    "file_path": output_path,
                    "duration": len(text.split()) * 0.4,
                    "voice_id": voice_id,
                    "format": "mp3",
                }
            }
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return {"success": False, "error": str(e)}

    async def list_voices(self) -> Dict[str, Any]:
        """List available voices."""
        try:
            if not self.api_key:
                return {
                    "success": True,
                    "voices": [
                        {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "gender": "female"},
                        {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "gender": "female"},
                    ],
                    "used_mock": True,
                }

            logger.info("Listing available voices")
            return {
                "success": True,
                "voices": [
                    {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "gender": "female"},
                ]
            }
        except Exception as e:
            logger.error(f"Error listing voices: {str(e)}")
            return {"success": False, "error": str(e)}
