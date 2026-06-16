"""Office365 Email Integration."""

import aiohttp
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseIntegration, ActivityEvent


class Office365Integration(BaseIntegration):
    """Office365 email monitoring integration."""

    API_BASE = "https://graph.microsoft.com/v1.0"

    async def authenticate(self) -> bool:
        """Authenticate with Office365 using OAuth2."""
        try:
            async with aiohttp.ClientSession() as session:
                auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
                data = {
                    "client_id": self.credentials.get("client_id"),
                    "client_secret": self.credentials.get("client_secret"),
                    "grant_type": "client_credentials",
                    "scope": "https://graph.microsoft.com/.default",
                }

                async with session.post(auth_url, data=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        self.credentials["access_token"] = result["access_token"]
                        self.is_authenticated = True
                        return True
                    return False
        except Exception as e:
            print(f"Office365 auth failed: {str(e)}")
            return False

    async def fetch_activities(self, hours: int = 24) -> List[ActivityEvent]:
        """Fetch email activities from Office365."""
        if not self.is_authenticated:
            await self.authenticate()

        activities = []

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.credentials['access_token']}",
                    "Content-Type": "application/json",
                }

                # Get mailbox audit events
                url = f"{self.API_BASE}/me/mailFolders/inbox/messages"
                params = {
                    "$top": 100,
                    "$filter": f"receivedDateTime ge {datetime.utcnow().isoformat()}",
                }

                async with session.get(url, headers=headers, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data.get("value", []):
                            event = self.normalize_activity(item)
                            activities.append(event)

        except Exception as e:
            print(f"Failed to fetch O365 activities: {str(e)}")

        return activities

    def normalize_activity(self, raw_event: Dict[str, Any]) -> ActivityEvent:
        """Normalize Office365 email event."""
        return ActivityEvent(
            user_id=raw_event.get("from", {}).get("emailAddress", {}).get("address", "unknown"),
            event_type="email",
            timestamp=datetime.fromisoformat(raw_event.get("receivedDateTime", "")),
            details={
                "subject": raw_event.get("subject"),
                "sender": raw_event.get("from", {}).get("emailAddress", {}).get("address"),
                "recipients": [
                    r.get("emailAddress", {}).get("address")
                    for r in raw_event.get("toRecipients", [])
                ],
                "has_attachments": raw_event.get("hasAttachments", False),
                "size": raw_event.get("bodyPreview", ""),
            },
            source_system="office365",
        )
