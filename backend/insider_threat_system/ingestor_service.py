import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import uvicorn
from insider_threat_system.db_init import SessionLocal, Email, SystemLog, MitigationLog

# Enterprise security API Key authorization
API_KEY = os.getenv("INGESTION_API_KEY", "threat_sentinel_default_key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

app = FastAPI(
    title="ThreatSentinel Ingestion Gateway",
    description="REST API interface to ingest corporate syslogs, emails, and system activity logs into the forensics engine.",
    version="1.0.0"
)

def verify_api_key(api_key: str = Security(api_key_header)):
    """Verifies the X-API-Key header to ensure logs are from trusted enterprise forwarders."""
    if not api_key or api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden: Invalid or missing X-API-Key credentials."
        )
    return api_key

# --- Request Schemas ---

class EmailPayload(BaseModel):
    id: str
    date: str
    user_id: str
    pc: str
    recipient: str
    sender: str
    attachments: int
    content: str
    origin_ip: Optional[str] = "127.0.0.1"
    location: Optional[str] = "Internal Corporate HQ"
    destination_ip: Optional[str] = "127.0.0.1"

class SystemLogPayload(BaseModel):
    user_id: str
    timestamp: str
    activity_type: str
    resource: str
    details: str
    ip: str
    location: str
    pc: str
    is_anomaly: Optional[int] = 0

# --- Routes ---

@app.get("/health", tags=["Health"])
def health_check():
    """Confirms the microservice status."""
    return {"status": "ONLINE", "timestamp": datetime.now().isoformat()}

@app.post("/ingest/email", status_code=status.HTTP_201_CREATED, tags=["Ingestion"])
def ingest_email(payload: EmailPayload, api_key: str = Security(verify_api_key)):
    """Ingests a captured corporate email directly into the SQL database in real-time."""
    db = SessionLocal()
    try:
        # Check date format
        try:
            parsed_date = datetime.strptime(payload.date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            parsed_date = datetime.now()

        email_entry = Email(
            id=payload.id,
            date=parsed_date,
            user_id=payload.user_id,
            pc=payload.pc,
            recipient=payload.recipient,
            sender=payload.sender,
            attachments=payload.attachments,
            content=payload.content,
            origin_ip=payload.origin_ip,
            location=payload.location,
            destination_ip=payload.destination_ip
        )
        db.add(email_entry)
        db.commit()
        return {"status": "SUCCESS", "message": f"Email log {payload.id} ingested successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during ingestion: {e}")
    finally:
        db.close()

@app.post("/ingest/system_logs", status_code=status.HTTP_201_CREATED, tags=["Ingestion"])
def ingest_system_logs(payload: SystemLogPayload, api_key: str = Security(verify_api_key)):
    """Ingests physical user activity system logs from local agents/SIEM integrations."""
    db = SessionLocal()
    try:
        try:
            parsed_time = datetime.strptime(payload.timestamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            parsed_time = datetime.now()

        log_entry = SystemLog(
            timestamp=parsed_time,
            user_id=payload.user_id,
            pc=payload.pc,
            activity_type=payload.activity_type,
            resource=payload.resource,
            details=payload.details,
            ip=payload.ip,
            location=payload.location,
            device=payload.pc,
            is_anomaly=payload.is_anomaly
        )
        db.add(log_entry)
        db.commit()
        return {"status": "SUCCESS", "message": f"System activity log logged successfully for {payload.user_id}."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Host on local network interface for corporate access
    uvicorn.run("ingestor_service:app", host="0.0.0.0", port=8000, reload=True)
