"""Integration manager for handling multiple data sources."""

from typing import Dict, List, Any
from database import SessionLocal
from models import Integration as IntegrationModel, ActivityLog
from datetime import datetime
from .office365 import Office365Integration
from .splunk import SplunkIntegration
from .active_directory import ActiveDirectoryIntegration


class IntegrationManager:
    """Manages all active integrations."""

    INTEGRATIONS = {
        "office365": Office365Integration,
        "splunk": SplunkIntegration,
        "active_directory": ActiveDirectoryIntegration,
    }

    @staticmethod
    async def sync_integration(tenant_id: str, integration_id: str) -> Dict[str, Any]:
        """Sync data from a single integration."""
        db = SessionLocal()
        try:
            integration = db.query(IntegrationModel).filter(
                IntegrationModel.id == integration_id,
                IntegrationModel.tenant_id == tenant_id,
            ).first()

            if not integration:
                return {"status": "error", "message": "Integration not found"}

            # Get the right integration class
            integration_class = IntegrationManager.INTEGRATIONS.get(integration.integration_type)
            if not integration_class:
                return {"status": "error", "message": "Integration type not supported"}

            # Create instance and sync
            integrator = integration_class(integration.credentials)
            activities = await integrator.fetch_activities()

            # Store activities in database
            count = 0
            for activity in activities:
                log = ActivityLog(
                    tenant_id=tenant_id,
                    employee_id=activity.user_id,
                    activity_type=activity.event_type,
                    source_system=activity.source_system,
                    timestamp=activity.timestamp,
                    details=activity.details,
                )
                db.add(log)
                count += 1

            db.commit()

            # Update last sync time
            integration.last_sync = datetime.utcnow()
            db.commit()

            return {
                "status": "success",
                "message": f"Synced {count} activities",
                "activities_count": count,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()

    @staticmethod
    async def sync_all_integrations(tenant_id: str) -> Dict[str, Any]:
        """Sync all active integrations for a tenant."""
        db = SessionLocal()
        try:
            integrations = db.query(IntegrationModel).filter(
                IntegrationModel.tenant_id == tenant_id,
                IntegrationModel.is_active == True,
            ).all()

            results = {}
            total_activities = 0

            for integration in integrations:
                result = await IntegrationManager.sync_integration(tenant_id, str(integration.id))
                results[integration.name] = result
                if result["status"] == "success":
                    total_activities += result.get("activities_count", 0)

            return {
                "status": "success",
                "total_integrations": len(integrations),
                "total_activities": total_activities,
                "results": results,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            db.close()
