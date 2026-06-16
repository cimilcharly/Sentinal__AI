"""Machine learning service for threat detection."""

import json
from typing import List, Dict, Any
from models import ActivityLog, RiskAssessment, EmployeeProfile
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd


class ThreatDetectionEngine:
    """ML engine for threat detection."""

    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = None

    def extract_features(self, activities: List[ActivityLog]) -> np.ndarray:
        """Extract features from activity logs."""
        if not activities:
            return np.array([]).reshape(0, 5)

        features = []
        for activity in activities:
            details = activity.details or {}
            feature_vector = [
                1 if activity.activity_type == "usb" else 0,
                1 if activity.activity_type == "file_access" else 0,
                1 if activity.activity_type == "process" else 0,
                1 if activity.timestamp.hour > 18 or activity.timestamp.hour < 6 else 0,
                details.get("size", 0) / (1024 * 1024),  # File size in MB
            ]
            features.append(feature_vector)

        return np.array(features)

    def score_activities(self, activities: List[ActivityLog]) -> float:
        """Score activities for anomaly detection."""
        if not activities:
            return 0.0

        features = self.extract_features(activities)
        if features.shape[0] == 0:
            return 0.0

        # Simple anomaly scoring
        anomalies = self.model.fit_predict(features)
        anomaly_count = (anomalies == -1).sum()
        anomaly_percentage = (anomaly_count / len(features)) * 100

        return min(100.0, anomaly_percentage * 2)

    def classify_threat_type(self, activities: List[ActivityLog], score: float) -> str:
        """Classify threat type based on activities and score."""
        if score > 70:
            for activity in activities:
                if "exfiltration" in str(activity.details).lower():
                    return "malicious"
            return "suspicious"
        elif score > 40:
            return "negligent"
        return "normal"

    def detect_suspicious_patterns(self, activities: List[ActivityLog]) -> Dict[str, Any]:
        """Detect specific suspicious patterns."""
        patterns = {
            "credential_leakage": False,
            "data_exfiltration": False,
            "privilege_escalation": False,
            "lateral_movement": False,
            "persistence": False,
        }

        for activity in activities:
            details = str(activity.details).lower()
            if any(keyword in details for keyword in ["password", "credential", "token", "key"]):
                patterns["credential_leakage"] = True
            if any(keyword in details for keyword in ["exfiltration", "download", "copy", "usb"]):
                patterns["data_exfiltration"] = True
            if "privilege" in details or "admin" in details:
                patterns["privilege_escalation"] = True

        return patterns
