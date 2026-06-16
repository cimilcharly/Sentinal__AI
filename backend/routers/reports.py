"""Report generation and management router."""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from database import SessionLocal
from models import User, Report, RiskAssessment
from schemas import ReportRequest, ReportResponse
from typing import List

router = APIRouter()


@router.post("/generate")
async def generate_report(request: ReportRequest, current_user: User = Depends()):
    """Generate security report for organization."""
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=request.days_lookback)

        # Gather metrics
        assessments = db.query(RiskAssessment).filter(
            RiskAssessment.tenant_id == current_user.tenant_id,
            RiskAssessment.assessment_date >= cutoff_date
        ).all()

        metrics = {
            "total_assessments": len(assessments),
            "flagged_count": len([a for a in assessments if a.flagged]),
            "malicious_count": len([a for a in assessments if a.threat_type == "malicious"]),
            "negligent_count": len([a for a in assessments if a.threat_type == "negligent"]),
            "avg_risk_score": sum([a.ml_anomaly_score for a in assessments]) / len(assessments) if assessments else 0,
            "report_period": f"{cutoff_date.date()} to {datetime.utcnow().date()}"
        }

        # Create report
        report = Report(
            tenant_id=current_user.tenant_id,
            report_type=request.report_type,
            title=request.title,
            content=generate_report_content(metrics, assessments),
            metrics=metrics,
            generated_by=current_user.id,
            created_at=datetime.utcnow()
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        return ReportResponse.from_orm(report)
    finally:
        db.close()


@router.get("/", response_model=List[ReportResponse])
async def list_reports(current_user: User = Depends(), limit: int = 10):
    """List organization reports."""
    db = SessionLocal()
    try:
        reports = db.query(Report).filter(
            Report.tenant_id == current_user.tenant_id
        ).order_by(Report.created_at.desc()).limit(limit).all()

        return [ReportResponse.from_orm(r) for r in reports]
    finally:
        db.close()


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, current_user: User = Depends()):
    """Get specific report."""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.tenant_id == current_user.tenant_id
        ).first()

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return ReportResponse.from_orm(report)
    finally:
        db.close()


@router.post("/{report_id}/send")
async def send_report(report_id: str, current_user: User = Depends()):
    """Send report (email integration)."""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.tenant_id == current_user.tenant_id
        ).first()

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Email sending logic would go here
        report.is_sent = True
        db.commit()

        return {"message": "Report sent successfully"}
    finally:
        db.close()


# ============ HELPER FUNCTIONS ============

def generate_report_content(metrics: dict, assessments: list) -> str:
    """Generate report HTML content."""
    html = f"""
    <html>
    <head><title>Security Report</title></head>
    <body>
        <h1>Insider Threat Detection Report</h1>
        <p><strong>Report Period:</strong> {metrics['report_period']}</p>

        <h2>Executive Summary</h2>
        <ul>
            <li>Total Assessments: {metrics['total_assessments']}</li>
            <li>Flagged Users: {metrics['flagged_count']}</li>
            <li>Malicious Threats: {metrics['malicious_count']}</li>
            <li>Negligent Activities: {metrics['negligent_count']}</li>
            <li>Average Risk Score: {metrics['avg_risk_score']:.1f}/100</li>
        </ul>

        <h2>Recommendations</h2>
        <ul>
            <li>Review flagged user activities</li>
            <li>Escalate malicious threats to security team</li>
            <li>Implement targeted user training for negligent behaviors</li>
        </ul>
    </body>
    </html>
    """
    return html
