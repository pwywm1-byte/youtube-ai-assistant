"""Voice generation service using gTTS (free, no local install required)."""

import logging
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


class VoiceService:
    """Generate audio narration from text using gTTS."""

    def __init__(self, output_dir: str = "./storage/audio"):
        """Initialize voice service."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info("Voice service initialized (gTTS)")

    def generate_audio(self, text: str, filename: str = "narration.mp3", lang: str = "en") -> Dict[str, Any]:
        """Generate an audio file from text using gTTS.

        Args:
            text: Text to convert to speech.
            filename: Output filename (must end with .mp3).
            lang: Language code (default 'en').

        Returns:
            Dict with file_path, duration estimate, and format.
        """
        try:
            from gtts import gTTS  # type: ignore
        except ImportError:
            raise ImportError("gTTS is not installed. Run: pip install gTTS")

        file_path = os.path.join(self.output_dir, filename)
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(file_path)

        word_count = len(text.split())
        estimated_duration = word_count / 2.2  # ~132 wpm

        logger.info(f"Audio generated: {file_path} (~{estimated_duration:.0f}s)")
        return {
            "file_path": file_path,
            "duration": estimated_duration,
            "bitrate": "128k",
            "format": "mp3",
            "word_count": word_count,
        }

    def generate_from_script(self, script: Dict[str, Any], output_filename: str = "voiceover.mp3") -> Dict[str, Any]:
        """Generate audio from a script dict produced by ScriptwritingAgent."""
        text = script.get("full_script") or script.get("content") or str(script)
        return self.generate_audio(text=text, filename=output_filename)
