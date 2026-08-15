"""Load environment variables safely using python-dotenv."""

from dotenv import load_dotenv
import os

# Load .env file if present (does not override already-set env vars)
load_dotenv()


def get_required(key: str) -> str:
    """Return the value of a required environment variable or raise an error."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            "Copy .env.example to .env and fill in the values."
        )
    return value


def get_optional(key: str, default: str = "") -> str:
    """Return the value of an optional environment variable."""
    return os.getenv(key, default)


# ---------------------------------------------------------------------------
# Grouped configuration accessors
# ---------------------------------------------------------------------------

class OpenAIConfig:
    api_key: str = get_optional("OPENAI_API_KEY")
    model: str = get_optional("OPENAI_MODEL", "gpt-4")
    temperature: float = float(get_optional("OPENAI_TEMPERATURE", "0.7"))


class ElevenLabsConfig:
    api_key: str = get_optional("ELEVENLABS_API_KEY")
    voice_id: str = get_optional("ELEVENLABS_VOICE_ID", "default_voice_id")


class YouTubeConfig:
    client_id: str = get_optional("YOUTUBE_CLIENT_ID")
    client_secret: str = get_optional("YOUTUBE_CLIENT_SECRET")
    channel_id: str = get_optional("YOUTUBE_CHANNEL_ID")
    refresh_token: str = get_optional("YOUTUBE_REFRESH_TOKEN")
