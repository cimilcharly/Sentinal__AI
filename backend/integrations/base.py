"""Base integration interface for all data sources."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class ActivityEvent:
    """Normalized activity event format."""
    def __init__(
        self,
        user_id: str,
        event_type: str,
        timestamp: datetime,
        details: Dict[str, Any],
        source_system: str,
    ):
        self.user_id = user_id
        self.event_type = event_type
        self.timestamp = timestamp
        self.details = details
        self.source_system = source_system

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "source_system": self.source_system,
        }


class BaseIntegration(ABC):
    """Abstract base class for all integrations."""

    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.is_authenticated = False

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the external service."""
        pass

    @abstractmethod
    async def fetch_activities(self, hours: int = 24) -> List[ActivityEvent]:
        """Fetch activities from the external service."""
        pass

    @abstractmethod
    def normalize_activity(self, raw_event: Dict[str, Any]) -> ActivityEvent:
        """Normalize raw event to standard format."""
        pass

    async def test_connection(self) -> bool:
        """Test if connection is working."""
        try:
            return await self.authenticate()
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False
