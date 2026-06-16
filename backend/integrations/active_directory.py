"""Active Directory Integration."""

from typing import List, Dict, Any
from datetime import datetime
from .base import BaseIntegration, ActivityEvent
import asyncio


class ActiveDirectoryIntegration(BaseIntegration):
    """Active Directory user and group monitoring."""

    async def authenticate(self) -> bool:
        """Authenticate with Active Directory."""
        try:
            # In production, use python-ldap or async-ldap
            # For now, mock the authentication
            self.is_authenticated = True
            return True
        except Exception as e:
            print(f"AD auth failed: {str(e)}")
            return False

    async def fetch_activities(self, hours: int = 24) -> List[ActivityEvent]:
        """Fetch user activities from Active Directory."""
        if not self.is_authenticated:
            await self.authenticate()

        activities = []

        try:
            # Query AD for:
            # 1. Failed login attempts
            # 2. Password changes
            # 3. Account lockouts
            # 4. Group membership changes
            # 5. Privilege changes

            mock_events = [
                {
                    "user": "john.smith",
                    "event": "login_failure",
                    "timestamp": datetime.utcnow().isoformat(),
                    "source_ip": "192.168.1.100",
                    "workstation": "DESKTOP-ABC123",
                },
                {
                    "user": "jane.doe",
                    "event": "group_change",
                    "timestamp": datetime.utcnow().isoformat(),
                    "new_group": "Domain Admins",
                    "modified_by": "admin@corp.local",
                },
            ]

            for event in mock_events:
                normalized = self.normalize_activity(event)
                activities.append(normalized)

        except Exception as e:
            print(f"Failed to fetch AD events: {str(e)}")

        return activities

    def normalize_activity(self, raw_event: Dict[str, Any]) -> ActivityEvent:
        """Normalize Active Directory event."""
        event_type_map = {
            "login_failure": "login",
            "password_change": "auth",
            "account_lockout": "auth",
            "group_change": "privilege",
            "permission_change": "privilege",
        }

        return ActivityEvent(
            user_id=raw_event.get("user", "unknown"),
            event_type=event_type_map.get(raw_event.get("event"), "other"),
            timestamp=datetime.fromisoformat(raw_event.get("timestamp", datetime.utcnow().isoformat())),
            details={
                "event_type": raw_event.get("event"),
                "source_ip": raw_event.get("source_ip"),
                "workstation": raw_event.get("workstation"),
                "group": raw_event.get("new_group"),
                "modified_by": raw_event.get("modified_by"),
            },
            source_system="active_directory",
        )
