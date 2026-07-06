"""Organization management router."""

from fastapi import APIRouter, Depends, HTTPException, status
from database import SessionLocal
from models import Tenant, User
from schemas import TenantCreate, TenantResponse, UserResponse
from typing import List
import secrets
from routers.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=TenantResponse)
async def get_organization(current_user: User = Depends(get_current_user)):
    """Get current organization details."""
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Organization not found")
        return TenantResponse.from_orm(tenant)
    finally:
        db.close()


@router.get("/users", response_model=List[UserResponse])
async def list_organization_users(current_user: User = Depends(get_current_user)):
    """List all users in organization."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view users")

    db = SessionLocal()
    try:
        users = db.query(User).filter(User.tenant_id == current_user.tenant_id).all()
        return [UserResponse.from_orm(u) for u in users]
    finally:
        db.close()


@router.post("/users/invite")
async def invite_user(email: str, role: str, current_user: User = Depends(get_current_user)):
    """Invite new user to organization."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can invite users")

    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # Create invitation (simplified - in production use email verification)
        new_user = User(
            tenant_id=current_user.tenant_id,
            email=email,
            role=role,
            full_name="",
            password_hash=""
        )
        db.add(new_user)
        db.commit()

        return {"message": f"Invitation sent to {email}"}
    finally:
        db.close()


@router.post("/api-keys")
async def generate_api_key(current_user: User = Depends(get_current_user)):
    """Generate new API key for organization."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can generate API keys")

    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Generate new API key
        api_key = f"sk_{secrets.token_hex(32)}"
        tenant.api_key = api_key
        db.commit()

        return {"api_key": api_key, "message": "New API key generated"}
    finally:
        db.close()
