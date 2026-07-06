import os
import sys

# Append backend directory to sys.path
sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from database import init_db, SessionLocal
from models import Tenant
from routers import auth, organizations, threats, reports, integrations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting InsiderThreat-AI SaaS application")
    init_db()
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="Sentinel AI API",
    description="Enterprise insider threat detection platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Security Middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ DEPENDENCY INJECTION ============

async def get_tenant_from_api_key(x_api_key: str = Header(None)) -> Tenant:
    """Extract tenant from API key header."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.api_key == x_api_key).first()
        if not tenant or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive API key",
            )
        return tenant
    finally:
        db.close()

# ============ ROUTES ============

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(
    organizations.router,
    prefix="/api/v1/organizations",
    tags=["Organizations"]
)
app.include_router(
    threats.router,
    prefix="/api/v1/threats",
    tags=["Threat Detection"]
)
app.include_router(
    reports.router,
    prefix="/api/v1/reports",
    tags=["Reports"]
)
app.include_router(
    integrations.router,
    prefix="/api/v1/integrations",
    tags=["Integrations"]
)


# ============ HEALTH CHECK ============

@app.get("/api/v1/health")
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "InsiderThreat-AI SaaS API",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API documentation."""
    return {
        "message": "InsiderThreat-AI SaaS API",
        "docs": "/docs",
        "health": "/health"
    }


# ============ ERROR HANDLERS ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "HTTP_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
