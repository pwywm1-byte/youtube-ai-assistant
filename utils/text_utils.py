"""Text utility functions."""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)


def sanitize_text(text: str) -> str:
    """Sanitize text by removing special characters."""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[^a-zA-Z0-9\s.!?,'-]", "", text)
    return text


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text."""
    words = text.lower().split()

    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
    }

    keywords = [
        word.strip(".,!?") for word in words if len(word) >= min_length and word not in stop_words
    ]

    return list(set(keywords))
