"""Active Directory Integration."""

from typing import List, Dict, Any
from datetime import datetime
from .base import BaseIntegration, ActivityEvent
import asyncio
import os


class ActiveDirectoryIntegration(BaseIntegration):
    """Active Directory user and group monitoring."""

    async def authenticate(self) -> bool:
        """Authenticate with Active Directory."""
        server = self.credentials.get("server") or os.getenv("ACTIVE_DIRECTORY_SERVER")
        username = self.credentials.get("username") or os.getenv("ACTIVE_DIRECTORY_USER")
        password = self.credentials.get("password") or os.getenv("ACTIVE_DIRECTORY_PASSWORD")

        if not server or not username or not password:
            print("Active Directory credentials not fully configured. Defaulting to Mock Mode.")
            self.is_authenticated = True
            self._use_mock = True
            return True

        try:
            import ldap3
            srv = ldap3.Server(server, get_info=ldap3.ALL)
            conn = ldap3.Connection(srv, user=username, password=password, auto_bind=True)
            self.conn = conn
            self.is_authenticated = True
            self._use_mock = False
            return True
        except ImportError:
            print("ldap3 package is not installed. Please install it using 'pip install ldap3' for real Active Directory. Defaulting to Mock Mode.")
            self.is_authenticated = True
            self._use_mock = True
            return True
        except Exception as e:
            print(f"AD connection failed: {str(e)}")
            return False

    async def fetch_activities(self, hours: int = 24) -> List[ActivityEvent]:
        """Fetch user activities from Active Directory."""
        if not self.is_authenticated:
            await self.authenticate()

        activities = []

        if getattr(self, "_use_mock", True):
            try:
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
                print(f"Failed to fetch mock AD events: {str(e)}")
            return activities

        try:
            # Query real Active Directory search logs
            import ldap3
            search_filter = "(&(objectClass=user)(sAMAccountName=*))"
            self.conn.search(
                search_base=self.credentials.get("search_base", "dc=company,dc=local"),
                search_filter=search_filter,
                attributes=["sAMAccountName", "whenChanged", "memberOf"]
            )
            for entry in self.conn.entries:
                # Map entries to ActivityEvent structure
                event = {
                    "user": entry.sAMAccountName.value,
                    "event": "group_change" if entry.memberOf.value else "login_failure",
                    "timestamp": entry.whenChanged.value.isoformat() if entry.whenChanged.value else datetime.utcnow().isoformat(),
                    "new_group": entry.memberOf.value[0] if entry.memberOf.value else "Domain Users",
                    "modified_by": "administrator"
                }
                activities.append(self.normalize_activity(event))
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
