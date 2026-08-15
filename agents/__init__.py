"""Agents module initialization."""

from abc import ABC, abstractmethod
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()
        self.execution_count = 0
        self.last_execution = None
        self.logger = logging.getLogger(f"agents.{name}")

    @abstractmethod
    async def execute(self, **kwargs):
        """Execute agent task."""
        pass

    def log_execution(self, status: str, details=None):
        """Log agent execution."""
        self.execution_count += 1
        self.last_execution = datetime.utcnow()
        log_message = f"[{self.name}] Execution #{self.execution_count}: {status}"
        if details:
            log_message += f" - {details}"
        if status == "success":
            self.logger.info(log_message)
        elif status == "error":
            self.logger.error(log_message)
        else:
            self.logger.warning(log_message)

    def get_status(self):
        """Get agent status."""
        return {
            "name": self.name,
            "description": self.description,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution,
            "created_at": self.created_at,
        }
