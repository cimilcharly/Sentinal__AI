"""SQLAlchemy ORM models for multi-tenant threat detection system."""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid
import enum


class ThreatType(str, enum.Enum):
    MALICIOUS = "malicious"
    NEGLIGENT = "negligent"
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SOC_ANALYST = "soc_analyst"
    SECURITY_OFFICER = "security_officer"
    AUDITOR = "auditor"


class Tenant(Base):
    """Organization/Company subscription."""
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False, index=True)
    subscription_tier = Column(String(50), default="starter")  # starter, professional, enterprise
    stripe_customer_id = Column(String(255), unique=True)
    api_key = Column(String(255), unique=True, index=True)
    data_retention_days = Column(Integer, default=90)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="tenant", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="tenant", cascade="all, delete-orphan")
    audit_trail = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="tenant", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    """User accounts within tenants."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255))
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.SOC_ANALYST)
    is_active = Column(Boolean, default=True)
    two_fa_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")
    __table_args__ = (
        # Unique constraint on email per tenant
        Column("unique_email_per_tenant", String, unique=True),
    )


class EmployeeProfile(Base):
    """Employee behavior baseline for detection."""
    __tablename__ = "employee_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(255), nullable=False, index=True)
    employee_name = Column(String(255))
    department = Column(String(255))
    role = Column(String(255))
    status = Column(String(50), default="active")  # active, inactive, ex-employee
    ocean_openness = Column(Float)
    ocean_conscientiousness = Column(Float)
    ocean_extraversion = Column(Float)
    ocean_agreeableness = Column(Float)
    ocean_neuroticism = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    """Raw activity logs from various sources."""
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(255), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # login, file_access, email, usb, process
    source_system = Column(String(100))  # office365, splunk, active_directory, aws
    timestamp = Column(DateTime, nullable=False, index=True)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="activity_logs")


class RiskAssessment(Base):
    """ML-generated risk scores and threat classification."""
    __tablename__ = "risk_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(String(255), nullable=False, index=True)
    assessment_date = Column(DateTime, nullable=False, index=True)
    ml_anomaly_score = Column(Float)  # 0-100 from Isolation Forest
    threat_type = Column(Enum(ThreatType), default=ThreatType.NORMAL)
    confidence = Column(Float)  # 0-1
    mitre_techniques = Column(JSON)  # List of MITRE ATT&CK techniques
    summary = Column(Text)  # Natural language summary
    detailed_analysis = Column(Text)  # LLM reasoning
    flagged = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="risk_assessments")


class AuditLog(Base):
    """Compliance and security audit trail."""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    status = Column(String(50))  # success, failure
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    tenant = relationship("Tenant", back_populates="audit_trail")


class Integration(Base):
    """Data source integrations configuration."""
    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    integration_type = Column(String(100), nullable=False)  # splunk, office365, okta, aws, etc
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    credentials = Column(JSON)  # Encrypted in production
    webhook_url = Column(String(255))
    last_sync = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="integrations")


class Report(Base):
    """Generated security reports."""
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(100))  # daily, weekly, monthly, custom
    title = Column(String(255))
    content = Column(Text)
    metrics = Column(JSON)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    scheduled_for = Column(DateTime)
    is_sent = Column(Boolean, default=False)

    tenant = relationship("Tenant", back_populates="reports")
