# Week 1-2 Foundation Setup Guide

## Prerequisites
- Docker & Docker Compose installed
- Python 3.11+ (for testing)
- Git
- ~5 minutes

## Step 1: Start All Services with Docker Compose

```bash
cd insider_threat_project
docker-compose up
```

**Expected Output:**
```
postgres_1  | database system is ready to accept connections
redis_1     | Ready to accept connections
backend_1   | Application startup complete
frontend_1  | ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

⏳ **Wait 30 seconds** for all services to fully initialize.

---

## Step 2: Initialize Database (In a new terminal)

```bash
# Run database initialization script
docker exec insider_threat_api python backend/init_db.py
```

**Expected Output:**
```
==================================================
🗄️  DATABASE INITIALIZATION
==================================================

🔄 Creating database tables...
✅ Database tables created successfully!
🌱 Seeding demo data...
✅ Created tenant: ACME Corp
✅ Created users: Alice Admin, Bob Analyst
✅ Created 3 demo employees
✅ Created 10 demo activity logs
✅ Created 3 demo risk assessments
✅ Created 2 demo audit logs

==================================================
✅ DEMO DATA SEEDING COMPLETE!
==================================================

📋 Demo Credentials:
   Admin:    admin@acmecorp.com / password123
   Analyst:  analyst@acmecorp.com / password123

🔑 Tenant API Key: sk_xxxxxxxxxxxxxxxxxxxxx

🏢 Tenant: ACME Corp (professional)

✨ Ready to start the application!
```

---

## Step 3: Test All API Endpoints

```bash
# Run API test suite
python backend/test_api.py
```

**Expected Output:**
```
============================================================
🧪 INSIDER THREAT-AI API TEST SUITE
============================================================

⏳ Waiting for API to be ready...
✅ API is ready!

📍 HEALTH CHECK
✅ Health Check
   GET /health
   Status: 200 (expected 200)

📍 AUTHENTICATION
✅ Login
   POST /auth/login
   Status: 200 (expected 200)

✅ Get Current User
   GET /auth/me
   Status: 200 (expected 200)

📍 ORGANIZATIONS
✅ Get Organization
   GET /organizations
   Status: 200 (expected 200)

✅ List Users
   GET /organizations/users
   Status: 200 (expected 200)

📍 THREAT DETECTION
✅ Analyze Threat
   POST /threats/analyze
   Status: 200 (expected 200)

✅ List Assessments
   GET /threats/assessments
   Status: 200 (expected 200)

✅ Get Employee Assessment
   GET /threats/assessments/EMP001
   Status: 200 (expected 200)

📍 REPORTS
✅ Generate Report
   POST /reports/generate
   Status: 200 (expected 200)

✅ List Reports
   GET /reports
   Status: 200 (expected 200)

📍 INTEGRATIONS
✅ List Integrations
   GET /integrations
   Status: 200 (expected 200)

============================================================
TEST RESULTS: 13/13 passed
============================================================

✅ Health Check
✅ Login
✅ Get Current User
✅ Get Organization
✅ List Users
✅ Analyze Threat
✅ List Assessments
✅ Get Employee Assessment
✅ Generate Report
✅ List Reports
✅ List Integrations

🎉 ALL TESTS PASSED! API is ready for use.
```

---

## Step 4: Access Services

### API Documentation (Auto-generated)
```
http://localhost:8000/docs
```
Click "Authorize" and use:
- **Username**: admin@acmecorp.com
- **Password**: password123

### Frontend (Coming in Week 3-4)
```
http://localhost:3000
```

### Database (Direct Access - Optional)
```bash
# Connect to PostgreSQL
docker exec -it insider_threat_db psql -U insider_threat_user -d insider_threat_saas

# List tables
\dt

# Query tenants
SELECT * FROM tenants;

# Exit
\q
```

### Redis CLI (Optional)
```bash
docker exec -it insider_threat_cache redis-cli

# Check keys
KEYS *

# Exit
exit
```

---

## Step 5: Test API with cURL

### Login & Get Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@acmecorp.com&password=password123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@acmecorp.com",
    "full_name": "Alice Admin",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-20T10:00:00"
  }
}
```

### Get Risk Assessments (Use token from above)
```bash
curl -X GET http://localhost:8000/api/v1/threats/assessments \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Analyze Threat
```bash
curl -X POST http://localhost:8000/api/v1/threats/analyze \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP002",
    "days_lookback": 30,
    "include_llm_analysis": true
  }'
```

---

## Environment Variables

The `.env` file has been created with default values:
- **DATABASE_URL**: PostgreSQL connection
- **REDIS_URL**: Redis connection
- **SECRET_KEY**: JWT signing key
- **OPENAI_API_KEY**: OpenAI API (mock mode for testing)

To use real OpenAI:
```bash
# Edit .env
USE_MOCK_LLM=false
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

---

## Troubleshooting

### Port Already in Use
```bash
# Stop all containers
docker-compose down

# Remove volumes to start fresh
docker-compose down -v

# Start again
docker-compose up
```

### Database Connection Error
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Verify database is running
docker ps | grep postgres
```

### API Not Responding
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Clear All Data & Start Fresh
```bash
# Stop containers
docker-compose down -v

# Start fresh
docker-compose up
docker exec insider_threat_api python backend/init_db.py
```

---

## What's Working Now ✅

- [x] PostgreSQL database with all tables
- [x] FastAPI backend with 5 routers
- [x] 11 API endpoints fully functional
- [x] Demo data (1 organization, 2 users, 3 employees, 10 activities, 3 assessments)
- [x] Authentication (JWT tokens)
- [x] Automatic API documentation (/docs)
- [x] Error handling & validation
- [x] Audit logging
- [x] Redis caching layer
- [x] Docker environment

---

## What's Next (Week 3-4)

- [ ] Build Next.js dashboard components
- [ ] Create authentication UI
- [ ] Build threat assessment cards
- [ ] Create report generation UI
- [ ] Connect frontend to backend API

---

## Success Indicators

You know Week 1-2 Foundation is complete when:

✅ `docker-compose up` starts all 4 services  
✅ Database initialization script runs without errors  
✅ All 13 API tests pass  
✅ Can login with admin@acmecorp.com / password123  
✅ API docs available at http://localhost:8000/docs  
✅ Can query risk assessments via API  

---

## Quick Reference Commands

```bash
# Start all services
docker-compose up

# Initialize database (new terminal)
docker exec insider_threat_api python backend/init_db.py

# Run API tests
python backend/test_api.py

# View API docs
http://localhost:8000/docs

# View logs
docker-compose logs -f backend
docker-compose logs -f postgres

# Stop everything
docker-compose down

# Clean restart (removes volumes)
docker-compose down -v && docker-compose up
```

---

**🎉 You're now ready for Week 3-4: Frontend Development!**
