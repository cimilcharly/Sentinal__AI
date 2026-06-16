"""Verify all imports and dependencies are available."""

import sys
from importlib import import_module

REQUIRED_MODULES = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "psycopg2",
    "pydantic",
    "jwt",
    "passlib",
    "email_validator",
    "redis",
    "stripe",
    "requests",
    "cryptography",
    "bcrypt",
    "sklearn",
    "torch",
    "openai",
]

def check_imports():
    """Check if all required modules are importable."""
    print("\n" + "="*60)
    print("🔍 VERIFYING PYTHON DEPENDENCIES")
    print("="*60 + "\n")

    missing = []

    for module in REQUIRED_MODULES:
        try:
            import_module(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing.append(module)

    print("\n" + "="*60)

    if missing:
        print(f"⚠️  Missing {len(missing)} dependencies:\n")
        for module in missing:
            print(f"   - {module}")
        print("\nInstall with:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies installed!")
        return True


def check_database():
    """Check if database connection works."""
    print("\n" + "="*60)
    print("🗄️  VERIFYING DATABASE CONNECTION")
    print("="*60 + "\n")

    try:
        from database import SessionLocal, engine
        from models import Base

        # Test connection
        with SessionLocal() as db:
            result = db.execute("SELECT 1")
            print("✅ PostgreSQL connection successful")

        # Check tables exist
        inspector = __import__("sqlalchemy", fromlist=["inspect"]).inspect(engine)
        tables = inspector.get_table_names()

        if tables:
            print(f"✅ Database has {len(tables)} tables")
            for table in tables[:5]:
                print(f"   - {table}")
            if len(tables) > 5:
                print(f"   ... and {len(tables) - 5} more")
        else:
            print("⚠️  No tables found. Run: python backend/init_db.py")
            return False

        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\nMake sure PostgreSQL is running:")
        print("   docker-compose up postgres")
        return False


def check_models():
    """Check if all models can be imported."""
    print("\n" + "="*60)
    print("📦 VERIFYING MODELS")
    print("="*60 + "\n")

    try:
        from models import (
            Tenant, User, EmployeeProfile, ActivityLog,
            RiskAssessment, AuditLog, Integration, Report,
            UserRole, ThreatType
        )
        print("✅ Tenant model")
        print("✅ User model")
        print("✅ EmployeeProfile model")
        print("✅ ActivityLog model")
        print("✅ RiskAssessment model")
        print("✅ AuditLog model")
        print("✅ Integration model")
        print("✅ Report model")
        print("✅ UserRole enum")
        print("✅ ThreatType enum")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {str(e)}")
        return False


def check_api():
    """Check if API can be imported."""
    print("\n" + "="*60)
    print("🚀 VERIFYING API APPLICATION")
    print("="*60 + "\n")

    try:
        from main import app
        print("✅ FastAPI application imported successfully")

        # Check routes
        routes = [route.path for route in app.routes]
        api_routes = [r for r in routes if r.startswith("/api")]
        print(f"✅ Found {len(api_routes)} API routes")

        return True
    except Exception as e:
        print(f"❌ API import failed: {str(e)}")
        return False


def main():
    """Run all checks."""
    results = {
        "Dependencies": check_imports(),
        "Models": check_models(),
        "Database": check_database(),
        "API": check_api(),
    }

    print("\n" + "="*60)
    print("📊 VERIFICATION SUMMARY")
    print("="*60 + "\n")

    for check, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {check}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL SYSTEMS GO! Ready to start the application.")
        print("\nStart with:")
        print("   docker-compose up")
        print("\nThen in another terminal:")
        print("   python backend/init_db.py")
        print("   python backend/test_api.py")
    else:
        print("⚠️  Some checks failed. See above for details.")
    print("="*60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
