"""Authentication and tenant isolation middleware."""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from datetime import datetime
import jwt
from database import SessionLocal
from models import User, Tenant, AuditLog

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


class TenantAuthMiddleware:
    """Middleware to enforce tenant isolation."""

    async def __call__(self, request: Request):
        """Validate tenant context for each request."""
        # Extract tenant ID from JWT or API key
        tenant_id = extract_tenant_id(request)

        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant context required"
            )

        # Store in request state for use in endpoints
        request.state.tenant_id = tenant_id

        # Log audit trail
        log_audit(request, tenant_id)


def extract_tenant_id(request: Request) -> str:
    """Extract tenant ID from request."""
    # Try JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("tenant_id")
        except jwt.InvalidTokenError:
            pass

    # Try API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        db = SessionLocal()
        try:
            tenant = db.query(Tenant).filter(Tenant.api_key == api_key).first()
            return str(tenant.id) if tenant else None
        finally:
            db.close()

    return None


def log_audit(request: Request, tenant_id: str):
    """Log API request to audit trail."""
    db = SessionLocal()
    try:
        audit_log = AuditLog(
            tenant_id=tenant_id,
            action=f"{request.method} {request.url.path}",
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", ""),
            status="pending",
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        print(f"Audit log error: {e}")
    finally:
        db.close()
