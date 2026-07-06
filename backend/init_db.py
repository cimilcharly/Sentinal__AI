"""Initialize database with sample data."""

import os
from dotenv import load_dotenv

# Load local environment file
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

from datetime import datetime, timedelta
import uuid
from database import SessionLocal, init_db, engine
from models import (
    Base, Tenant, User, EmployeeProfile, ActivityLog,
    RiskAssessment, AuditLog, Integration, UserRole, ThreatType
)
from security import PasswordSecurity
import secrets


def init_database():
    """Initialize all tables."""
    print("🔄 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def seed_demo_data():
    """Seed database with demo data for testing."""
    db = SessionLocal()

    try:
        # Check if demo data already exists
        existing_tenant = db.query(Tenant).filter(Tenant.name == "ACME Corp").first()
        if existing_tenant:
            print("⚠️  Demo data already exists. Skipping seed...")
            return

        print("🌱 Seeding demo data...")

        # Create demo tenant
        tenant = Tenant(
            id=uuid.uuid4(),
            name="ACME Corp",
            subscription_tier="professional",
            stripe_customer_id="cus_demo_123",
            api_key=f"sk_{secrets.token_hex(32)}",
            data_retention_days=90,
            is_active=True
        )
        db.add(tenant)
        db.commit()
        print(f"✅ Created tenant: {tenant.name}")

        # Create demo users
        admin_user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="admin@acmecorp.com",
            password_hash=PasswordSecurity.hash_password("password123"),
            full_name="Alice Admin",
            role=UserRole.ADMIN,
            is_active=True
        )

        analyst_user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email="analyst@acmecorp.com",
            password_hash=PasswordSecurity.hash_password("password123"),
            full_name="Bob Analyst",
            role=UserRole.SOC_ANALYST,
            is_active=True
        )

        db.add(admin_user)
        db.add(analyst_user)
        db.commit()
        print(f"✅ Created users: {admin_user.full_name}, {analyst_user.full_name}")

        # Create demo employees
        employees = [
            EmployeeProfile(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                employee_id="EMP001",
                employee_name="John Smith",
                department="Engineering",
                role="Senior Developer",
                status="active",
                ocean_openness=0.7,
                ocean_conscientiousness=0.8,
                ocean_extraversion=0.6,
                ocean_agreeableness=0.7,
                ocean_neuroticism=0.3
            ),
            EmployeeProfile(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                employee_id="EMP002",
                employee_name="Jane Doe",
                department="Finance",
                role="Financial Analyst",
                status="active",
                ocean_openness=0.6,
                ocean_conscientiousness=0.9,
                ocean_extraversion=0.5,
                ocean_agreeableness=0.8,
                ocean_neuroticism=0.2
            ),
            EmployeeProfile(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                employee_id="EMP003",
                employee_name="Rick Wilson",
                department="Operations",
                role="Operations Manager",
                status="ex-employee",
                ocean_openness=0.5,
                ocean_conscientiousness=0.7,
                ocean_extraversion=0.8,
                ocean_agreeableness=0.6,
                ocean_neuroticism=0.4
            ),
        ]
        db.add_all(employees)
        db.commit()
        print(f"✅ Created {len(employees)} demo employees")

        # Create demo activity logs
        now = datetime.utcnow()
        activities = []

        for emp in employees[:2]:  # Activity for active employees only
            for i in range(5):
                activity = ActivityLog(
                    id=uuid.uuid4(),
                    tenant_id=tenant.id,
                    employee_id=emp.employee_id,
                    activity_type=["login", "file_access", "email", "usb", "process"][i % 5],
                    source_system="office365",
                    timestamp=now - timedelta(hours=i),
                    details={
                        "location": "New York, NY",
                        "ip_address": "192.168.1.100",
                        "device": "LAPTOP-ABC123",
                        "size": 5 * 1024 * 1024 if i % 3 == 0 else None
                    }
                )
                activities.append(activity)

        db.add_all(activities)
        db.commit()
        print(f"✅ Created {len(activities)} demo activity logs")

        # Create demo risk assessments
        assessments = [
            RiskAssessment(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                employee_id="EMP001",
                assessment_date=now,
                ml_anomaly_score=35.5,
                threat_type=ThreatType.NORMAL,
                confidence=0.92,
                mitre_techniques=["T1078", "T1133"],
                summary="Normal user behavior detected. Login patterns consistent with baseline.",
                detailed_analysis="Employee login activity shows normal geographic patterns. File access volumes within expected range.",
                flagged=False
            ),
            RiskAssessment(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                employee_id="EMP002",
                assessment_date=now,
                ml_anomaly_score=72.3,
                threat_type=ThreatType.SUSPICIOUS,
                confidence=0.85,
                mitre_techniques=["T1020", "T1567"],
                summary="Suspicious data transfer activity detected after business hours.",
                detailed_analysis="Employee performed large file transfers to external email at 11:45 PM. Pattern inconsistent with normal behavior.",
                flagged=True
            ),
            RiskAssessment(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                employee_id="EMP003",
                assessment_date=now - timedelta(days=10),
                ml_anomaly_score=88.9,
                threat_type=ThreatType.MALICIOUS,
                confidence=0.95,
                mitre_techniques=["T1098", "T1020", "T1567"],
                summary="Ex-employee account still active with unauthorized access patterns.",
                detailed_analysis="Former employee (Rick Wilson) account terminated 10 days ago but still accessing sensitive financial documents. Password likely compromised.",
                flagged=True
            ),
        ]
        db.add_all(assessments)
        db.commit()
        print(f"✅ Created {len(assessments)} demo risk assessments")

        # Create demo audit logs
        audit_logs = [
            AuditLog(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                user_id=admin_user.id,
                action="login",
                resource_type="authentication",
                ip_address="203.0.113.42",
                user_agent="Mozilla/5.0",
                status="success",
                timestamp=now - timedelta(hours=1)
            ),
            AuditLog(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                user_id=analyst_user.id,
                action="view_assessment",
                resource_type="risk_assessment",
                resource_id="EMP002",
                ip_address="203.0.113.43",
                status="success",
                timestamp=now - timedelta(minutes=30)
            ),
        ]
        db.add_all(audit_logs)
        db.commit()
        print(f"✅ Created {len(audit_logs)} demo audit logs")

        print("\n" + "="*50)
        print("✅ DEMO DATA SEEDING COMPLETE!")
        print("="*50)
        print(f"\n📋 Demo Credentials:")
        print(f"   Admin:    admin@acmecorp.com / password123")
        print(f"   Analyst:  analyst@acmecorp.com / password123")
        print(f"\n🔑 Tenant API Key: {tenant.api_key}")
        print(f"\n🏢 Tenant: {tenant.name} ({tenant.subscription_tier})")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🗄️  DATABASE INITIALIZATION")
    print("="*50 + "\n")

    init_database()
    seed_demo_data()

    print("\n✨ Ready to start the application!")
    print("   Run: uvicorn backend.main:app --reload")
