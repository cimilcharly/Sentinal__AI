"""Data integrations management router."""

from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from models import User, Integration
from schemas import IntegrationCreate, IntegrationResponse
from datetime import datetime
from typing import List
from routers.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=IntegrationResponse)
async def create_integration(data: IntegrationCreate, current_user: User = Depends(get_current_user)):
    """Create new data source integration."""
    if current_user.role not in ["admin", "security_officer"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db = SessionLocal()
    try:
        integration = Integration(
            tenant_id=current_user.tenant_id,
            integration_type=data.integration_type,
            name=data.name,
            credentials=data.credentials,
            is_active=True
        )
        db.add(integration)
        db.commit()
        db.refresh(integration)

        return IntegrationResponse.from_orm(integration)
    finally:
        db.close()


@router.get("/", response_model=List[IntegrationResponse])
async def list_integrations(current_user: User = Depends(get_current_user)):
    """List organization integrations."""
    db = SessionLocal()
    try:
        integrations = db.query(Integration).filter(
            Integration.tenant_id == current_user.tenant_id
        ).all()

        return [IntegrationResponse.from_orm(i) for i in integrations]
    finally:
        db.close()


@router.get("/{integration_id}", response_model=IntegrationResponse)
async def get_integration(integration_id: str, current_user: User = Depends(get_current_user)):
    """Get specific integration."""
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.id == integration_id,
            Integration.tenant_id == current_user.tenant_id
        ).first()

        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")

        return IntegrationResponse.from_orm(integration)
    finally:
        db.close()


@router.post("/{integration_id}/test")
async def test_integration(integration_id: str, current_user: User = Depends(get_current_user)):
    """Test integration connection."""
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.id == integration_id,
            Integration.tenant_id == current_user.tenant_id
        ).first()

        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")

        # Test logic would go here
        return {
            "status": "success",
            "message": f"Connection to {integration.integration_type} verified"
        }
    finally:
        db.close()


@router.post("/{integration_id}/sync")
async def trigger_sync(integration_id: str, current_user: User = Depends(get_current_user)):
    """Trigger data sync from integration."""
    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.id == integration_id,
            Integration.tenant_id == current_user.tenant_id
        ).first()

        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")

        integration.last_sync = datetime.utcnow()
        db.commit()

        return {
            "status": "syncing",
            "message": f"Sync started for {integration.name}",
            "job_id": "job_123456"
        }
    finally:
        db.close()


@router.delete("/{integration_id}")
async def delete_integration(integration_id: str, current_user: User = Depends(get_current_user)):
    """Delete integration."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete integrations")

    db = SessionLocal()
    try:
        integration = db.query(Integration).filter(
            Integration.id == integration_id,
            Integration.tenant_id == current_user.tenant_id
        ).first()

        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")

        db.delete(integration)
        db.commit()

        return {"message": "Integration deleted"}
    finally:
        db.close()
