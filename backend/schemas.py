"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


# ============ AUTH SCHEMAS ============

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ TENANT SCHEMAS ============

class TenantCreate(BaseModel):
    name: str
    subscription_tier: str = "starter"
    data_retention_days: int = 90


class TenantResponse(BaseModel):
    id: UUID
    name: str
    subscription_tier: str
    api_key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TenantUpdate(BaseModel):
    subscription_tier: Optional[str] = None
    data_retention_days: Optional[int] = None
    is_active: Optional[bool] = None


# ============ ACTIVITY LOG SCHEMAS ============

class ActivityLogCreate(BaseModel):
    employee_id: str
    activity_type: str
    source_system: str
    timestamp: datetime
    details: Dict[str, Any]


class ActivityLogResponse(BaseModel):
    id: UUID
    employee_id: str
    activity_type: str
    source_system: str
    timestamp: datetime
    details: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ RISK ASSESSMENT SCHEMAS ============

class RiskAssessmentResponse(BaseModel):
    id: UUID
    employee_id: str
    assessment_date: datetime
    ml_anomaly_score: float
    threat_type: str
    confidence: float
    mitre_techniques: Optional[List[str]]
    summary: str
    detailed_analysis: Optional[str]
    flagged: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ThreatAnalysisRequest(BaseModel):
    employee_id: str
    days_lookback: int = 30
    include_llm_analysis: bool = True


# ============ INTEGRATION SCHEMAS ============

class IntegrationCreate(BaseModel):
    integration_type: str
    name: str
    credentials: Dict[str, Any]


class IntegrationResponse(BaseModel):
    id: UUID
    integration_type: str
    name: str
    is_active: bool
    last_sync: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ REPORT SCHEMAS ============

class ReportResponse(BaseModel):
    id: UUID
    report_type: str
    title: str
    content: str
    metrics: Dict[str, Any]
    created_at: datetime
    is_sent: bool

    class Config:
        from_attributes = True


class ReportRequest(BaseModel):
    report_type: str
    title: str
    days_lookback: int = 30
    include_graphs: bool = True


# ============ ERROR SCHEMAS ============

class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    timestamp: datetime


class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]]
