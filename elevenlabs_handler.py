"""ElevenLabs text-to-speech handler."""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests


class ElevenLabsHandler:
    """Handle ElevenLabs voice generation operations."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        voice_id: Optional[str] = None,
        model_id: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = voice_id or os.getenv("ELEVENLABS_VOICE_ID")
        self.model_id = model_id or os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
        self.timeout = timeout
        self.base_url = "https://api.elevenlabs.io/v1"

        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is not set.")

    def _headers(self) -> Dict[str, str]:
        return {
            "xi-api-key": self.api_key,
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
        }

    def _auth_headers(self) -> Dict[str, str]:
        return {"xi-api-key": self.api_key}

    def list_voices(self) -> Dict[str, Any]:
        """List voices available on the ElevenLabs account."""
        response = requests.get(
            f"{self.base_url}/voices",
            headers=self._auth_headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def text_to_speech(
        self,
        text: str,
        output_path: str,
        voice_id: Optional[str] = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True,
    ) -> str:
        """Generate speech audio from text and write it to output_path."""
        selected_voice = voice_id or self.voice_id
        if not selected_voice:
            raise ValueError("ELEVENLABS_VOICE_ID is not set.")
        if not text.strip():
            raise ValueError("Text must not be empty.")

        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost,
            },
        }

        response = requests.post(
            f"{self.base_url}/text-to-speech/{selected_voice}",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()

        with open(output_path, "wb") as output_file:
            output_file.write(response.content)
        return output_path

    def generate_voice(self, text: str, output_path: str, voice_id: Optional[str] = None) -> str:
        """Alias for text_to_speech."""
        return self.text_to_speech(text=text, output_path=output_path, voice_id=voice_id)
