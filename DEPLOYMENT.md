# InsiderThreat-AI SaaS Deployment Guide

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15 (or use Docker)

### Setup

1. **Clone and install dependencies:**
```bash
cd insider_threat_project
cp .env.example .env
pip install -r requirements.txt
cd frontend && npm install
```

2. **Start development environment:**
```bash
docker-compose up
```

3. **Access the application:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

---

## Production Deployment

### AWS Deployment (ECS + RDS)

1. **Prepare Docker images:**
```bash
docker build -t insider-threat-api:latest .
docker build -t insider-threat-frontend:latest ./frontend
```

2. **Push to ECR:**
```bash
aws ecr create-repository --repository-name insider-threat-api
aws ecr push insider-threat-api:latest
```

3. **Deploy with CloudFormation/Terraform:**
- RDS PostgreSQL (Multi-AZ)
- ElastiCache Redis
- ECS Fargate tasks
- Application Load Balancer
- CloudFront CDN

### Google Cloud Deployment (Cloud Run + Cloud SQL)

```bash
gcloud run deploy insider-threat-api \
  --image gcr.io/PROJECT_ID/insider-threat-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=postgresql://...
```

### Azure Deployment (App Service + Azure Database)

```bash
az webapp create --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name insider-threat-api
```

---

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add column X"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Monitoring & Observability

### Sentry (Error Tracking)
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### Datadog (Metrics & Logs)
```
DD_TRACE_ENABLED=true
DD_AGENT_HOST=localhost
```

### Health Checks
```bash
curl http://localhost:8000/health
```

---

## Security Checklist

- [ ] Enable HTTPS/TLS 1.3
- [ ] Configure WAF rules
- [ ] Set up VPC isolation
- [ ] Enable database encryption
- [ ] Configure API rate limiting
- [ ] Set up DDoS protection
- [ ] Enable audit logging
- [ ] Configure backup retention

---

## Scaling Configuration

### Database
- Connection pool: 20 (adjust per load)
- Read replicas for analytics
- Automated backups (daily)

### Backend
- Auto-scale: 2-10 instances
- CPU threshold: 70%
- Memory threshold: 80%
- Health check: /health every 30s

### Frontend
- CDN: CloudFront/Akamai
- Edge caching: 1 hour for static assets
- Gzip compression enabled

---

## Cost Optimization

- Reserved instances for baseline load
- Spot instances for burst capacity
- Data retention policies (90 days default)
- Log aggregation and rotation
- Database query optimization

---

## Support & SLA

- Tier 1 (Starter): Community support
- Tier 2 (Professional): 24/7 email support, 8-hour response
- Tier 3 (Enterprise): Dedicated support team, 1-hour response, 99.99% SLA
