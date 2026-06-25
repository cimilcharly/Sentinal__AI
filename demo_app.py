#!/usr/bin/env python3
"""
Sentinel AI - Interactive Demo
Shows the key features of the insider threat detection system
"""

import json
from datetime import datetime, timedelta
import random
from typing import List
import sys
import io

# Enable UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class ThreatDetectionDemo:
    """Demonstrates Sentinel AI's threat detection capabilities"""

    def __init__(self):
        self.employees = [
            {"id": 1, "name": "John Smith", "dept": "Engineering", "role": "Senior Dev"},
            {"id": 2, "name": "Sarah Johnson", "dept": "Sales", "role": "Account Manager"},
            {"id": 3, "name": "Mike Chen", "dept": "Finance", "role": "Analyst"},
            {"id": 4, "name": "Lisa Brown", "dept": "HR", "role": "HR Manager"},
            {"id": 5, "name": "David Wilson", "dept": "Security", "role": "Security Officer"},
        ]

        self.activity_log = []
        self.risk_assessments = []

    def simulate_activities(self):
        """Simulate user activities that trigger threat detection"""
        activities = [
            {
                "employee_id": 1,
                "timestamp": datetime.now(),
                "activity_type": "file_access",
                "details": "Accessed 500 employee records at 2 AM",
                "risk_score": 85,
                "alert": True
            },
            {
                "employee_id": 2,
                "timestamp": datetime.now() - timedelta(hours=1),
                "activity_type": "email_forward",
                "details": "Forwarded customer list to external email",
                "risk_score": 92,
                "alert": True
            },
            {
                "employee_id": 3,
                "timestamp": datetime.now() - timedelta(hours=2),
                "activity_type": "data_download",
                "details": "Downloaded financial reports to USB drive",
                "risk_score": 78,
                "alert": True
            },
            {
                "employee_id": 4,
                "timestamp": datetime.now() - timedelta(hours=3),
                "activity_type": "access_denied",
                "details": "Multiple failed login attempts to payroll system",
                "risk_score": 45,
                "alert": False
            },
            {
                "employee_id": 5,
                "timestamp": datetime.now() - timedelta(hours=4),
                "activity_type": "system_access",
                "details": "Normal security audit log review",
                "risk_score": 15,
                "alert": False
            },
        ]
        self.activity_log = activities
        return activities

    def analyze_threats(self) -> List[dict]:
        """Analyze activities and generate threat assessments"""
        threats = []

        for activity in self.activity_log:
            if activity["risk_score"] >= 70:
                emp = next(e for e in self.employees if e["id"] == activity["employee_id"])

                threat = {
                    "id": len(threats) + 1,
                    "employee": emp["name"],
                    "department": emp["dept"],
                    "severity": "HIGH" if activity["risk_score"] >= 85 else "MEDIUM",
                    "risk_score": activity["risk_score"],
                    "activity": activity["activity_type"],
                    "description": activity["details"],
                    "timestamp": activity["timestamp"].isoformat(),
                    "mitre_tactic": self._get_mitre_tactic(activity["activity_type"]),
                    "recommended_action": self._get_recommendation(activity["risk_score"]),
                    "status": "unreviewed"
                }
                threats.append(threat)

        self.risk_assessments = threats
        return threats

    def _get_mitre_tactic(self, activity_type):
        """Map activity to MITRE ATT&CK tactic"""
        mapping = {
            "file_access": "T1087 - Account Discovery",
            "email_forward": "T1567 - Exfiltration Over Web Service",
            "data_download": "T1020 - Automated Exfiltration",
            "access_denied": "T1110 - Brute Force",
            "system_access": "T1078 - Valid Accounts"
        }
        return mapping.get(activity_type, "Unknown")

    def _get_recommendation(self, risk_score):
        """Get recommended action based on risk score"""
        if risk_score >= 90:
            return "[!!!] IMMEDIATE: Block account and investigate"
        elif risk_score >= 80:
            return "[!!] URGENT: Notify SOC team and restrict access"
        elif risk_score >= 70:
            return "[*] REVIEW: Flag for security review"
        else:
            return "[i] MONITOR: Continue observation"

    def generate_report(self):
        """Generate a security report"""
        high_threats = [t for t in self.risk_assessments if t["severity"] == "HIGH"]
        medium_threats = [t for t in self.risk_assessments if t["severity"] == "MEDIUM"]

        report = {
            "report_id": f"REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "period": "Last 24 hours",
            "organization": "ACME Corporation",
            "summary": {
                "total_activities": len(self.activity_log),
                "threats_detected": len(self.risk_assessments),
                "high_severity": len(high_threats),
                "medium_severity": len(medium_threats),
                "critical_alerts": len([t for t in high_threats if t["risk_score"] >= 85])
            },
            "top_threats": high_threats[:3],
            "recommendations": [
                "Review and revoke access for high-risk employees",
                "Implement additional email monitoring",
                "Audit recent file access patterns",
                "Schedule security awareness training"
            ]
        }
        return report


def print_header(title):
    """Print formatted header"""
    print("\n" + "-"*70)
    print(f"  {title}")
    print("-"*70)


def print_threat_card(threat):
    """Print a formatted threat card"""
    severity_marker = "[!!!]" if threat["severity"] == "HIGH" else "[!!]"
    print(f"\n{severity_marker} [{threat['severity']}] {threat['employee']} - Risk Score: {threat['risk_score']}")
    print(f"   Department: {threat['department']}")
    print(f"   Activity: {threat['activity'].replace('_', ' ').title()}")
    print(f"   Details: {threat['description']}")
    print(f"   MITRE: {threat['mitre_tactic']}")
    print(f"   Action: {threat['recommended_action']}")


def main():
    """Run the interactive demo"""

    print("\n")
    print("[" + "="*68 + "]")
    print("     SENTINEL AI - INSIDER THREAT DETECTION PLATFORM")
    print("     Enterprise-Grade Threat Detection")
    print("[" + "="*68 + "]")

    # Initialize demo
    demo = ThreatDetectionDemo()

    # Step 1: Show employee profiles
    print_header(" STEP 1: EMPLOYEE BASELINE PROFILES")
    print("\nMonitored employees in your organization:")
    for emp in demo.employees:
        print(f"  • {emp['name']} ({emp['dept']}) - {emp['role']}")

    # Step 2: Simulate activities
    print_header(" STEP 2: SIMULATING USER ACTIVITIES")
    print("\nAnalyzing user activities in real-time...")
    activities = demo.simulate_activities()

    print(f"\nProcessed {len(activities)} activities")
    for activity in activities:
        emp = next(e for e in demo.employees if e["id"] == activity["employee_id"])
        alert_emoji = "" if activity["alert"] else "✅"
        print(f"  {alert_emoji} {emp['name']}: {activity['details']} (Risk: {activity['risk_score']})")

    # Step 3: Threat analysis
    print_header(" STEP 3: AI-POWERED THREAT ANALYSIS")
    print("\nRunning ML + LLM hybrid analysis...")
    threats = demo.analyze_threats()

    print(f"\n✓ Analysis complete. {len(threats)} threats detected.")

    for threat in threats:
        print_threat_card(threat)

    # Step 4: Generate report
    print_header(" STEP 4: THREAT REPORT GENERATION")
    report = demo.generate_report()

    print(f"\nReport ID: {report['report_id']}")
    print(f"Generated: {report['generated_at']}")
    print(f"\n EXECUTIVE SUMMARY:")
    print(f"  • Total Activities Analyzed: {report['summary']['total_activities']}")
    print(f"  • Threats Detected: {report['summary']['threats_detected']}")
    print(f"  • High Severity: {report['summary']['high_severity']}")
    print(f"  • Critical Alerts: {report['summary']['critical_alerts']}")

    print(f"\n RECOMMENDATIONS:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")

    # Step 5: Show API endpoints
    print_header(" STEP 5: API ENDPOINTS AVAILABLE")

    endpoints = [
        ("POST", "/api/v1/auth/login", "User authentication"),
        ("GET", "/api/v1/organizations", "Get organization details"),
        ("GET", "/api/v1/organizations/users", "List organization users"),
        ("POST", "/api/v1/threats/analyze", "Analyze threat from activity"),
        ("GET", "/api/v1/threats/assessments", "List all threat assessments"),
        ("GET", "/api/v1/threats/assessments/{id}", "Get threat assessment details"),
        ("POST", "/api/v1/reports/generate", "Generate security report"),
        ("GET", "/api/v1/reports", "List reports"),
        ("POST", "/api/v1/integrations", "Create data integration"),
        ("GET", "/api/v1/integrations", "List integrations"),
        ("POST", "/api/v1/integrations/{id}/sync", "Sync data from integration"),
    ]

    print("\nCore API Endpoints:")
    for method, endpoint, description in endpoints:
        method_color = "POST" if method == "POST" else "GET"
        print(f"  [{method_color:4}] {endpoint:40} - {description}")

    # Step 6: Show features
    print_header("✨ KEY FEATURES")

    features = {
        " AI Detection": [
            "ML-based anomaly detection (Isolation Forest)",
            "GPT-4 powered threat classification",
            "MITRE ATT&CK mapping",
        ],
        " Security": [
            "JWT & API Key authentication",
            "AES-256 encryption at rest",
            "Multi-tenant architecture",
            "Comprehensive audit logging",
        ],
        " Analytics": [
            "Real-time dashboard",
            "Risk scoring (0-100)",
            "Custom reports",
            "Threat history tracking",
        ],
        " Integrations": [
            "Office 365 email monitoring",
            "Splunk SIEM integration",
            "Active Directory sync",
            "AWS CloudTrail support",
        ],
    }

    for category, items in features.items():
        print(f"\n{category}")
        for item in items:
            print(f"  ✓ {item}")

    # Step 7: Database schema
    print_header(" DATABASE SCHEMA")

    tables = {
        "tenants": "Organization accounts (multi-tenant)",
        "users": "Admin and analyst accounts",
        "employee_profiles": "Employee baselines for anomaly detection",
        "activity_logs": "Raw user activities and events",
        "risk_assessments": "Threat detections and classifications",
        "audit_logs": "Compliance and audit trail",
        "integrations": "Connected data sources",
        "reports": "Generated security reports",
    }

    print("\nDatabase Tables:")
    for table, purpose in tables.items():
        print(f"   {table:20} - {purpose}")

    # Step 8: Show demo results as JSON
    print_header(" SAMPLE JSON RESPONSE")

    print("\nSample Threat Detection Response:")
    print(json.dumps(threats[0] if threats else {}, indent=2))

    # Final summary
    print_header(" DEMO COMPLETE")

    print("""
The Sentinel AI platform provides:
  ✅ Real-time insider threat detection
  ✅ AI-powered risk analysis
  ✅ Beautiful web dashboard
  ✅ RESTful API for integrations
  ✅ Enterprise security features
  ✅ Production-ready infrastructure

To run the full application:
  1. Start services: docker-compose up
  2. Access dashboard: http://localhost:3000
  3. API docs: http://localhost:8000/docs
  4. Login with: admin@acmecorp.com / password123
    """)

    print("\n" + "="*70)
    print("Sentinel AI - Protecting enterprises from insider threats ️")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
