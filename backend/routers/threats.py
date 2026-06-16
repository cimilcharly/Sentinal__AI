"""Threat detection and analysis router."""

from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime, timedelta
from database import SessionLocal
from models import User, RiskAssessment, ActivityLog, ThreatType
from schemas import ThreatAnalysisRequest, RiskAssessmentResponse
from typing import List, Optional
import json

router = APIRouter()


@router.post("/analyze")
async def analyze_threat(request: ThreatAnalysisRequest, current_user: User = Depends()):
    """Analyze threat for a user."""
    db = SessionLocal()
    try:
        # Get recent activity logs
        cutoff_date = datetime.utcnow() - timedelta(days=request.days_lookback)
        activities = db.query(ActivityLog).filter(
            ActivityLog.tenant_id == current_user.tenant_id,
            ActivityLog.employee_id == request.employee_id,
            ActivityLog.timestamp >= cutoff_date
        ).all()

        if not activities:
            raise HTTPException(status_code=404, detail="No activities found for user")

        # Create risk assessment
        risk_score = calculate_risk_score(activities)
        threat_type = classify_threat(activities, risk_score)

        assessment = RiskAssessment(
            tenant_id=current_user.tenant_id,
            employee_id=request.employee_id,
            assessment_date=datetime.utcnow(),
            ml_anomaly_score=risk_score,
            threat_type=threat_type,
            confidence=0.85,
            summary=generate_summary(activities, threat_type),
            flagged=risk_score > 70
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        return RiskAssessmentResponse.from_orm(assessment)
    finally:
        db.close()


@router.get("/assessments", response_model=List[RiskAssessmentResponse])
async def list_risk_assessments(
    current_user: User = Depends(),
    days: int = Query(7, ge=1, le=90),
    threat_type: Optional[str] = None,
    flagged_only: bool = False
):
    """List risk assessments for organization."""
    db = SessionLocal()
    try:
        query = db.query(RiskAssessment).filter(
            RiskAssessment.tenant_id == current_user.tenant_id,
            RiskAssessment.assessment_date >= datetime.utcnow() - timedelta(days=days)
        )

        if threat_type:
            query = query.filter(RiskAssessment.threat_type == threat_type)
        if flagged_only:
            query = query.filter(RiskAssessment.flagged == True)

        assessments = query.order_by(RiskAssessmentResponse.assessment_date.desc()).all()
        return [RiskAssessmentResponse.from_orm(a) for a in assessments]
    finally:
        db.close()


@router.get("/assessments/{employee_id}", response_model=RiskAssessmentResponse)
async def get_employee_assessment(employee_id: str, current_user: User = Depends()):
    """Get latest assessment for an employee."""
    db = SessionLocal()
    try:
        assessment = db.query(RiskAssessment).filter(
            RiskAssessment.tenant_id == current_user.tenant_id,
            RiskAssessment.employee_id == employee_id
        ).order_by(RiskAssessment.assessment_date.desc()).first()

        if not assessment:
            raise HTTPException(status_code=404, detail="No assessment found")

        return RiskAssessmentResponse.from_orm(assessment)
    finally:
        db.close()


@router.post("/assessments/{assessment_id}/acknowledge")
async def acknowledge_assessment(assessment_id: str, current_user: User = Depends()):
    """Acknowledge a risk assessment."""
    db = SessionLocal()
    try:
        assessment = db.query(RiskAssessment).filter(
            RiskAssessment.id == assessment_id,
            RiskAssessment.tenant_id == current_user.tenant_id
        ).first()

        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")

        assessment.is_acknowledged = True
        assessment.acknowledged_by = current_user.id
        assessment.acknowledged_at = datetime.utcnow()
        db.commit()

        return {"message": "Assessment acknowledged"}
    finally:
        db.close()


# ============ HELPER FUNCTIONS ============

def calculate_risk_score(activities: list) -> float:
    """Calculate ML-based risk score from activities."""
    score = 0.0

    if not activities:
        return 0.0

    suspicious_types = ["usb", "process", "file_access"]
    after_hours_activities = sum(1 for a in activities if a.timestamp.hour > 18 or a.timestamp.hour < 6)

    score += len([a for a in activities if a.activity_type in suspicious_types]) * 5
    score += after_hours_activities * 3
    score += len([a for a in activities if "exfiltration" in str(a.details).lower()]) * 20

    return min(100.0, score)


def classify_threat(activities: list, risk_score: float) -> str:
    """Classify threat type."""
    if risk_score > 70:
        for activity in activities:
            if "exfiltration" in str(activity.details).lower():
                return ThreatType.MALICIOUS.value
        return ThreatType.SUSPICIOUS.value
    elif risk_score > 40:
        return ThreatType.NEGLIGENT.value
    return ThreatType.NORMAL.value


def generate_summary(activities: list, threat_type: str) -> str:
    """Generate natural language summary."""
    if not activities:
        return "No suspicious activity detected."

    total = len(activities)
    suspicious = len([a for a in activities if a.activity_type in ["usb", "process"]])

    return f"User performed {total} activities in monitoring period. {suspicious} suspicious actions detected. Classification: {threat_type}."
