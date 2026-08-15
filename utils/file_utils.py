"""File utility functions."""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def save_file(content: bytes, file_path: str, overwrite: bool = True) -> bool:
    """Save file to disk."""
    try:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        if os.path.exists(file_path) and not overwrite:
            logger.warning(f"File already exists: {file_path}")
            return False
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {str(e)}")
        return False


def load_file(file_path: str) -> Optional[bytes]:
    """Load file from disk."""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return None
        
        with open(file_path, "rb") as f:
            content = f.read()
        
        logger.info(f"File loaded: {file_path}")
        return content
        
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {str(e)}")
        return None


def delete_file(file_path: str) -> bool:
    """Delete file from disk."""
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return False
        
        os.remove(file_path)
        logger.info(f"File deleted: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False
