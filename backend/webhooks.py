"""Webhook handling for real-time integrations."""

import hmac
import hashlib
from typing import Dict, Any
from fastapi import HTTPException, status
from datetime import datetime
from database import SessionLocal
from models import ActivityLog


class WebhookHandler:
    """Handle incoming webhooks from integrations."""

    WEBHOOK_SECRETS = {}  # Load from environment

    @staticmethod
    def verify_signature(payload: str, signature: str, secret: str) -> bool:
        """Verify webhook signature."""
        expected_sig = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_sig)

    @staticmethod
    def handle_office365_webhook(
        tenant_id: str,
        payload: Dict[str, Any],
        signature: str
    ) -> Dict[str, Any]:
        """Handle Office365 webhook payload."""
        # Verify signature
        if not WebhookHandler.verify_signature(
            str(payload),
            signature,
            WebhookHandler.WEBHOOK_SECRETS.get("office365", "")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )

        db = SessionLocal()
        try:
            events = payload.get("value", [])
            created_count = 0

            for event in events:
                # Extract email metadata
                log = ActivityLog(
                    tenant_id=tenant_id,
                    employee_id=event.get("from", {}).get("emailAddress", {}).get("address", "unknown"),
                    activity_type="email",
                    source_system="office365_webhook",
                    timestamp=datetime.fromisoformat(event.get("receivedDateTime", "")),
                    details={
                        "subject": event.get("subject"),
                        "recipients": event.get("toRecipients", []),
                        "has_attachments": event.get("hasAttachments"),
                        "size": event.get("size"),
                        "event_id": event.get("id"),
                    },
                )
                db.add(log)
                created_count += 1

            db.commit()

            return {
                "status": "success",
                "events_processed": created_count,
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process webhook: {str(e)}"
            )
        finally:
            db.close()

    @staticmethod
    def handle_splunk_webhook(
        tenant_id: str,
        payload: Dict[str, Any],
        signature: str
    ) -> Dict[str, Any]:
        """Handle Splunk webhook payload."""
        # Verify signature
        if not WebhookHandler.verify_signature(
            str(payload),
            signature,
            WebhookHandler.WEBHOOK_SECRETS.get("splunk", "")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )

        db = SessionLocal()
        try:
            events = payload.get("results", [])
            created_count = 0

            for event in events:
                log = ActivityLog(
                    tenant_id=tenant_id,
                    employee_id=event.get("user", "unknown"),
                    activity_type=event.get("event_type", "other"),
                    source_system="splunk_webhook",
                    timestamp=datetime.fromisoformat(event.get("timestamp", "")),
                    details={
                        "source_ip": event.get("src"),
                        "destination_ip": event.get("dest"),
                        "action": event.get("action"),
                        "event_type": event.get("event_type"),
                    },
                )
                db.add(log)
                created_count += 1

            db.commit()

            return {
                "status": "success",
                "events_processed": created_count,
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process webhook: {str(e)}"
            )
        finally:
            db.close()
