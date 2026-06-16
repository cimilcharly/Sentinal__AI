"""Webhook endpoints for real-time data ingestion."""

from fastapi import APIRouter, Header, Body
from typing import Dict, Any
from webhooks import WebhookHandler

router = APIRouter()


@router.post("/office365")
async def receive_office365_webhook(
    tenant_id: str,
    x_signature: str = Header(None),
    payload: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """Receive Office365 email events via webhook."""
    return WebhookHandler.handle_office365_webhook(tenant_id, payload, x_signature)


@router.post("/splunk")
async def receive_splunk_webhook(
    tenant_id: str,
    x_signature: str = Header(None),
    payload: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    """Receive Splunk security events via webhook."""
    return WebhookHandler.handle_splunk_webhook(tenant_id, payload, x_signature)


@router.get("/test")
async def test_webhook() -> Dict[str, Any]:
    """Test endpoint for webhook connectivity."""
    return {
        "status": "webhook_service_active",
        "endpoints": ["/office365", "/splunk"],
    }
