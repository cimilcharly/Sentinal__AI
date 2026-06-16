"""Splunk SIEM Integration."""

import aiohttp
from typing import List, Dict, Any
from datetime import datetime, timedelta
from .base import BaseIntegration, ActivityEvent


class SplunkIntegration(BaseIntegration):
    """Splunk SIEM monitoring integration."""

    async def authenticate(self) -> bool:
        """Authenticate with Splunk."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.credentials['host']}/services/auth/login"
                data = {
                    "username": self.credentials["username"],
                    "password": self.credentials["password"],
                }

                async with session.post(url, data=data, ssl=False) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        # Extract session key from response
                        if "sessionKey" in text:
                            self.is_authenticated = True
                            return True
                    return False
        except Exception as e:
            print(f"Splunk auth failed: {str(e)}")
            return False

    async def fetch_activities(self, hours: int = 24) -> List[ActivityEvent]:
        """Fetch security events from Splunk."""
        if not self.is_authenticated:
            await self.authenticate()

        activities = []

        try:
            async with aiohttp.ClientSession() as session:
                # Search for authentication and file access events
                search_query = f"""
                    search (eventtype=authentication OR eventtype=file_access)
                    earliest=-{hours}h
                    | fields user, event_type, timestamp, src, dest, action
                    | head 1000
                """

                url = f"{self.credentials['host']}/services/search/jobs/export"
                params = {
                    "search": search_query,
                    "output_mode": "json",
                    "earliest_time": f"-{hours}h",
                }

                async with session.get(
                    url, params=params, auth=aiohttp.BasicAuth(
                        self.credentials["username"],
                        self.credentials["password"]
                    ), ssl=False
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for result in data.get("results", []):
                            event = self.normalize_activity(result)
                            activities.append(event)

        except Exception as e:
            print(f"Failed to fetch Splunk events: {str(e)}")

        return activities

    def normalize_activity(self, raw_event: Dict[str, Any]) -> ActivityEvent:
        """Normalize Splunk event."""
        event_type_map = {
            "authentication": "login",
            "file_access": "file_access",
            "process_creation": "process",
            "network_connection": "network",
        }

        return ActivityEvent(
            user_id=raw_event.get("user", "unknown"),
            event_type=event_type_map.get(raw_event.get("event_type"), "other"),
            timestamp=datetime.fromisoformat(raw_event.get("timestamp", datetime.utcnow().isoformat())),
            details={
                "source_ip": raw_event.get("src"),
                "destination_ip": raw_event.get("dest"),
                "action": raw_event.get("action"),
                "event_type": raw_event.get("event_type"),
                "raw_data": raw_event,
            },
            source_system="splunk",
        )
