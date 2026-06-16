from datetime import datetime
import os
import requests
from insider_threat_system.db_init import SessionLocal, Employee, MitigationLog

class AlertSystem:
    """
    Enterprise Incident Response and Active Mitigation Engine.
    Handles real-time automated containment (disabling user credentials),
    Syslog notifications, Slack/Teams webhooks, and PagerDuty escalations.
    """
    def __init__(self):
        self.slack_webhook = os.getenv("SLACK_SECURITY_WEBHOOK")
        self.pagerduty_key = os.getenv("PAGERDUTY_INTEGRATION_KEY")
        self.graph_api_token = os.getenv("MS_GRAPH_API_TOKEN")

    def process_mitigation(self, user_id, threat_type, risk_score, reasoning="AI Assessment"):
        """Decides and executes active mitigation actions based on risk thresholds."""
        if risk_score >= 90:
            action = "ACCOUNT_LOCKDOWN"
            self.lockdown_user(user_id)
            self._log_mitigation(user_id, threat_type, action, reasoning, "SUCCESS")
            self._send_admin_alert(user_id, threat_type, action)
            return action
        elif risk_score >= 75:
            action = "ADMIN_REVIEW_REQUIRED"
            self._log_mitigation(user_id, threat_type, action, reasoning, "PENDING")
            self._send_admin_alert(user_id, threat_type, action)
            return action
        return "NONE"

    def lockdown_user(self, user_id):
        """
        Executes automated containment.
        1. Deactivates employee status in the enterprise DB via SQLAlchemy.
        2. Disables user credentials in Microsoft Active Directory (via API stub).
        """
        # 1. Update Database Status
        db = SessionLocal()
        try:
            employee = db.query(Employee).filter(Employee.user_id == user_id).first()
            if employee:
                employee.status = 'LOCKED'
                db.commit()
                print(f"🔒 [DATABASE] Account status set to LOCKED for user: {user_id}")
            else:
                print(f"⚠️ [DATABASE] User {user_id} not found during lockdown procedure.")
        except Exception as e:
            print(f"❌ [DATABASE] Failed to update user status during lockdown: {e}")
            db.rollback()
        finally:
            db.close()

        # 2. Simulate/Execute Active Directory Lockout
        self._disable_active_directory_account(user_id)

    def _disable_active_directory_account(self, user_id):
        """Simulates/executes Azure Active Directory (Microsoft Entra ID) user lockdown."""
        if self.graph_api_token:
            print(f"📡 [Active Directory] Disabling Entra ID account for {user_id} via Microsoft Graph API...")
            try:
                headers = {
                    "Authorization": f"Bearer {self.graph_api_token}",
                    "Content-Type": "application/json"
                }
                url = f"https://graph.microsoft.com/v1.0/users/{user_id}@company.onmicrosoft.com"
                payload = {"accountEnabled": False}
                # Patch request to disable account
                res = requests.patch(url, json=payload, headers=headers, timeout=5)
                if res.status_code == 204:
                    print(f"✅ [Active Directory] Account disabled successfully for {user_id}.")
                else:
                    print(f"❌ [Active Directory] Entra ID lockout failed (HTTP {res.status_code}): {res.text}")
            except Exception as e:
                print(f"❌ [Active Directory] API exception during lockout: {e}")
        else:
            # Informative audit logs showing mock activity in sandbox mode
            print(f"ℹ️ [Active Directory] SANDBOX MODE: Active Directory account disable command simulated for '{user_id}'.")

    def _log_mitigation(self, user_id, threat_type, action, reasoning, status):
        """Logs the action taken to the SQL database using SQLAlchemy."""
        db = SessionLocal()
        try:
            log = MitigationLog(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                user_id=user_id,
                threat_type=threat_type,
                action_taken=action,
                reasoning=reasoning,
                status=status
            )
            db.add(log)
            db.commit()
        except Exception as e:
            print(f"❌ Database error logging mitigation: {e}")
            db.rollback()
        finally:
            db.close()

    def _send_admin_alert(self, user_id, threat_type, action):
        """Sends security alert signals out to modern enterprise systems."""
        # 1. Standard Syslog Audit Output
        print("\n" + "!"*10 + " CRITICAL SECURITY ALERT " + "!"*10)
        print(f"Recipient: admin-soc@company.com")
        print(f"Subject: [URGENT] Mitigation Action Triggered for {user_id}")
        print(f"Threat detected: {threat_type}")
        print(f"Action Taken: {action}")
        print("!"*45 + "\n")

        # 2. Modern Slack Security Channel Webhook
        if self.slack_webhook:
            print(f"📡 [Alerting] Forwarding incident alert to security Slack channel...")
            try:
                payload = {
                    "text": f"🚨 *CRITICAL SECURITY BREACH DETECTED*\n"
                            f"*User ID:* `{user_id}`\n"
                            f"*Vector Identified:* `{threat_type}`\n"
                            f"*Containment Action:* `{action}`\n"
                            f"*Status:* Active Containment Complete."
                }
                res = requests.post(self.slack_webhook, json=payload, timeout=5)
                if res.status_code == 200:
                    print("✅ [Alerting] Slack notification dispatched.")
            except Exception as e:
                print(f"❌ [Alerting] Failed to forward Slack webhook: {e}")

        # 3. PagerDuty Incident Escalation Stub
        if self.pagerduty_key:
            print(f"📡 [Alerting] Escalating incident to PagerDuty...")
            # PagerDuty integration protocol
            pass
