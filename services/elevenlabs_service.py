"""ElevenLabs TTS service for voice generation."""

import logging
import os
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.elevenlabs.io/v1"
_DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel
_DEFAULT_MODEL = "eleven_monolingual_v1"
_CHUNK_SIZE = 1024


class ElevenLabsService:
    """Handle ElevenLabs API operations for text-to-speech.

    When no API key is configured the service operates in **mock mode**:
    it returns metadata describing the expected output without making real
    network calls, so the pipeline can run end-to-end during development.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        model: str = _DEFAULT_MODEL,
    ):
        self.api_key = api_key
        self.voice_id = voice_id or _DEFAULT_VOICE_ID
        self.model = model
        self._mock = not bool(api_key)
        mode = "mock" if self._mock else "authenticated"
        logger.info("ElevenLabs Service initialised (%s), voice: %s", mode, self.voice_id)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {"xi-api-key": self.api_key or "", "Accept": "audio/mpeg"}

    def _estimate_duration(self, text: str) -> float:
        """Rough estimate: ~130 words per minute for ElevenLabs voices."""
        return round(len(text.split()) / 130 * 60, 1)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        output_path: str = "output/voiceover.mp3",
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> Dict[str, Any]:
        """Generate speech from *text* and save to *output_path*.

        Returns metadata including estimated duration.
        Falls back to mock response when no API key is set.
        """
        vid = voice_id or self.voice_id
        duration_est = self._estimate_duration(text)

        if self._mock:
            logger.warning("ElevenLabs mock mode — not generating real audio")
            return {
                "success": True,
                "audio": {
                    "file_path": output_path,
                    "duration": duration_est,
                    "voice_id": vid,
                    "format": "mp3",
                },
                "used_mock": True,
            }

        url = f"{_BASE_URL}/text-to-speech/{vid}"
        payload = {
            "text": text,
            "model_id": self.model,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
            },
        }
        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=120)
            response.raise_for_status()

            os.makedirs(
                os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True
            )
            with open(output_path, "wb") as fh:
                for chunk in response.iter_content(chunk_size=_CHUNK_SIZE):
                    fh.write(chunk)

            logger.info("Speech generated: %s (%.1fs)", output_path, duration_est)
            return {
                "success": True,
                "audio": {
                    "file_path": output_path,
                    "duration": duration_est,
                    "voice_id": vid,
                    "format": "mp3",
                },
            }
        except requests.HTTPError as exc:
            logger.error("ElevenLabs HTTP error: %s", exc)
            return {"success": False, "error": str(exc)}
        except Exception as exc:
            logger.error("ElevenLabs error: %s", exc)
            return {"success": False, "error": str(exc)}

    async def list_voices(self) -> Dict[str, Any]:
        """Return available voices from ElevenLabs."""
        _default_voices = [
            {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "gender": "female"},
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "gender": "female"},
            {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "gender": "male"},
            {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "gender": "female"},
            {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "gender": "male"},
        ]

        if self._mock:
            return {"success": True, "voices": _default_voices, "used_mock": True}

        try:
            response = requests.get(
                f"{_BASE_URL}/voices",
                headers={"xi-api-key": self.api_key or ""},
                timeout=30,
            )
            response.raise_for_status()
            raw = response.json()
            voices: List[Dict[str, Any]] = [
                {
                    "id": v["voice_id"],
                    "name": v["name"],
                    "gender": v.get("labels", {}).get("gender", "unknown"),
                }
                for v in raw.get("voices", [])
            ]
            return {"success": True, "voices": voices}
        except Exception as exc:
            logger.error("Failed to list voices: %s", exc)
            return {"success": False, "error": str(exc)}

    async def get_user_info(self) -> Dict[str, Any]:
        """Return current user/subscription info."""
        if self._mock:
            return {"success": True, "user": {}, "used_mock": True}
        try:
            response = requests.get(
                f"{_BASE_URL}/user",
                headers={"xi-api-key": self.api_key or ""},
                timeout=30,
            )
            response.raise_for_status()
            return {"success": True, "user": response.json()}
        except Exception as exc:
            logger.error("Failed to get user info: %s", exc)
            return {"success": False, "error": str(exc)}
