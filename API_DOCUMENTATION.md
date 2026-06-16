# InsiderThreat-AI SaaS API Documentation

## Base URL
```
https://api.insiderthreat-ai.com/api/v1
```

## Authentication

All API requests require authentication via JWT token or API key.

### JWT Token Authentication
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=yourpassword"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "soc_analyst"
  }
}
```

### API Key Authentication
```bash
curl http://localhost:8000/api/v1/threats/assessments \
  -H "X-API-Key: sk_xxxxxxxxxxxxx"
```

---

## Endpoints

### Authentication

#### POST /auth/login
Login with email and password.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password"
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user info.

**Request:**
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {token}"
```

---

### Organizations

#### GET /organizations
Get current organization.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ACME Corp",
  "subscription_tier": "professional",
  "api_key": "sk_...",
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

#### GET /organizations/users
List organization users (admin only).

**Response:**
```json
[
  {
    "id": "uuid",
    "email": "analyst@acme.com",
    "full_name": "John Analyst",
    "role": "soc_analyst",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

#### POST /organizations/users/invite
Invite new user (admin only).

**Request:**
```json
{
  "email": "newuser@acme.com",
  "role": "soc_analyst"
}
```

---

### Threats

#### POST /threats/analyze
Analyze threat for employee.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/threats/analyze \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "days_lookback": 30,
    "include_llm_analysis": true
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "employee_id": "EMP001",
  "assessment_date": "2024-01-20T10:00:00Z",
  "ml_anomaly_score": 75.5,
  "threat_type": "suspicious",
  "confidence": 0.85,
  "mitre_techniques": ["T1071", "T1567"],
  "summary": "User performed unusual file access patterns",
  "detailed_analysis": "LLM analysis...",
  "flagged": true,
  "created_at": "2024-01-20T10:00:00Z"
}
```

#### GET /threats/assessments
List risk assessments.

**Query Parameters:**
- `days` (int): Days to look back (default: 7)
- `threat_type` (str): Filter by threat type
- `flagged_only` (bool): Show only flagged assessments

**Response:**
```json
[
  {
    "id": "uuid",
    "employee_id": "EMP001",
    "ml_anomaly_score": 75.5,
    "threat_type": "suspicious",
    "flagged": true,
    "created_at": "2024-01-20T10:00:00Z"
  }
]
```

#### GET /threats/assessments/{employee_id}
Get latest assessment for employee.

---

### Reports

#### POST /reports/generate
Generate security report.

**Request:**
```json
{
  "report_type": "weekly",
  "title": "Weekly Security Report",
  "days_lookback": 7,
  "include_graphs": true
}
```

**Response:**
```json
{
  "id": "uuid",
  "report_type": "weekly",
  "title": "Weekly Security Report",
  "content": "<html>...",
  "metrics": {
    "total_assessments": 150,
    "flagged_count": 12,
    "malicious_count": 2,
    "avg_risk_score": 35.5
  },
  "created_at": "2024-01-20T10:00:00Z"
}
```

#### GET /reports
List reports.

**Query Parameters:**
- `limit` (int): Number of reports (default: 10)

#### POST /reports/{report_id}/send
Send report via email.

---

### Integrations

#### POST /integrations
Create integration.

**Request:**
```json
{
  "integration_type": "office365",
  "name": "Office 365 Email",
  "credentials": {
    "client_id": "xxx",
    "client_secret": "xxx",
    "tenant_id": "xxx"
  }
}
```

#### GET /integrations
List integrations.

#### POST /integrations/{integration_id}/test
Test integration connection.

#### POST /integrations/{integration_id}/sync
Trigger data sync.

---

## Error Codes

| Code | Message | Action |
|------|---------|--------|
| 400 | Bad Request | Check request parameters |
| 401 | Unauthorized | Provide valid token/API key |
| 403 | Forbidden | Check user role/permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Reduce request frequency |
| 500 | Internal Error | Contact support |

---

## Rate Limiting

- **Starter tier**: 100 requests/hour
- **Professional tier**: 1,000 requests/hour
- **Enterprise tier**: Unlimited

Response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

---

## Webhooks

Enable webhooks in organization settings to receive real-time notifications.

### Event Types
- `threat.detected` - New threat detected
- `assessment.completed` - Assessment completed
- `integration.synced` - Integration sync completed

### Webhook Structure
```json
{
  "event_type": "threat.detected",
  "timestamp": "2024-01-20T10:00:00Z",
  "data": {
    "threat_id": "uuid",
    "employee_id": "EMP001",
    "threat_type": "malicious"
  }
}
```
