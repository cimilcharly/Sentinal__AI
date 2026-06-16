# 📊 MONITORING & OBSERVABILITY SETUP

## Production Monitoring Stack

### Tools Configuration

#### 1. Sentry (Error Tracking)
```python
# backend/config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxxx@sentry.io/xxxx",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment="production",
    release="1.0.0"
)
```

#### 2. Datadog (Metrics & Logs)
```python
# backend/main.py
from ddtrace import tracer, patch_all

patch_all()  # Auto-instrument

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log to Datadog
    logger.info(
        "request",
        extra={
            "duration_ms": process_time * 1000,
            "path": request.url.path,
            "method": request.method,
            "status": response.status_code
        }
    )
    return response
```

#### 3. ELK Stack (Log Aggregation)
```yaml
# docker-compose.yml additions
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node
  ports:
    - "9200:9200"

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
  depends_on:
    - elasticsearch

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
```

---

## Key Metrics to Monitor

### API Performance
```
Metric                  Target      Alert
-------------------------------------------
Response Time           <500ms      >1s
Error Rate             <0.1%       >0.5%
Request Throughput     >100/s      -
P95 Latency            <1s         >2s
P99 Latency            <2s         >5s
```

### Database Performance
```
Metric                  Target      Alert
-------------------------------------------
Query Time             <100ms      >500ms
Connection Pool        <80%        >90%
Disk Usage             <80%        >90%
Backup Status          Daily       Failed
Replication Lag        <1s         >5s
```

### Infrastructure
```
Metric                  Target      Alert
-------------------------------------------
CPU Usage              <70%        >85%
Memory Usage           <80%        >90%
Disk Usage             <80%        >90%
Network I/O            Normal      Spike
Load Balancer Health   100%        <100%
```

### Application
```
Metric                  Target      Alert
-------------------------------------------
Active Users           Track        -
API Key Usage          Monitor      Anomaly
Integration Health     >95%        <95%
Sync Success Rate      >99%        <99%
Feature Usage          Track        -
```

---

## Alert Configuration

### Critical Alerts (Page Oncall)
```
if API_DOWN for >1 minute:
  - Slack: Red alert
  - PagerDuty: Page oncall
  - Email: Team notification

if ERROR_RATE >1%:
  - Slack: Red alert
  - PagerDuty: Page oncall
  - Auto-rollback: Optional

if DB_UNAVAILABLE:
  - Slack: Critical alert
  - PagerDuty: Page oncall
  - Failover: Initiate
```

### Warning Alerts (Slack Notification)
```
if RESPONSE_TIME >1s:
  - Slack: Yellow notification
  - Monitoring: Check capacity

if ERROR_RATE >0.5%:
  - Slack: Yellow notification
  - Development: Investigate

if DISK_USAGE >85%:
  - Slack: Yellow notification
  - Operations: Plan cleanup

if MEMORY_USAGE >80%:
  - Slack: Yellow notification
  - Development: Optimize
```

---

## Logging Strategy

### Log Levels
```
DEBUG:   Development only
INFO:    All requests, key events
WARNING: Potential issues
ERROR:   Actual errors
FATAL:   System failures
```

### What to Log
```
API Requests:
  - Timestamp
  - User ID
  - Endpoint
  - Method
  - Status
  - Response time
  - Error (if any)

Integration Events:
  - Sync start/end
  - Records processed
  - Errors encountered
  - Duration

Authentication:
  - Login attempt
  - Success/failure
  - User ID
  - Timestamp
  - IP address

Security Events:
  - Failed attempts
  - Unusual activity
  - Configuration changes
  - Data access
```

---

## Dashboard Visualization

### Main Dashboard (Real-Time)
```
┌─────────────────────────────────────────┐
│         InsiderThreat-AI Status         │
├─────────────────────────────────────────┤
│ API Status: 🟢 UP                       │
│ Database: 🟢 HEALTHY                    │
│ Integrations: 🟢 SYNCED                 │
├─────────────────────────────────────────┤
│ Response Time: 245ms (🟢 Good)          │
│ Error Rate: 0.03% (🟢 Good)             │
│ Requests/min: 450 (🟢 Normal)           │
├─────────────────────────────────────────┤
│ Active Users: 12                        │
│ Threats Detected (Today): 34            │
│ Reports Generated: 8                    │
└─────────────────────────────────────────┘
```

### Performance Dashboard
```
- API Latency Over Time (Chart)
- Error Rate Trend (Chart)
- Request Volume (Chart)
- Database Query Time (Chart)
- Top Slow Endpoints (Table)
- Error Types (Pie chart)
```

### Integration Dashboard
```
- Office365 Sync Status
- Splunk Event Count
- Active Directory Health
- AWS CloudTrail Events
- Webhook Processing Time
- Last Sync Timestamps
```

---

## Incident Response

### On-Call Rotation
```
Week 1: Engineer A
Week 2: Engineer B
Week 3: Engineer C
Week 4: Founder

On-call duties:
- Monitor alerts
- Respond to critical issues
- 15-minute response target
- Escalate if needed
```

### Incident Severity

```
P1 - Critical (Page immediately)
  - System down
  - Data loss
  - Security breach
  - Revenue impact

P2 - High (Respond in 1 hour)
  - Degraded performance
  - Customer-blocking issue
  - Major feature broken

P3 - Medium (Respond in 4 hours)
  - Minor bugs
  - UI issues
  - Non-critical features

P4 - Low (Respond in 24 hours)
  - Documentation
  - Polish
  - Non-urgent
```

### Incident Runbook

```
1. Acknowledge Alert
   - Slack: React with ✅
   - PagerDuty: Acknowledge incident

2. Assess Severity
   - Check current impact
   - Determine P-level
   - Notify stakeholders

3. Investigate
   - Check logs/metrics
   - Identify root cause
   - Scope of impact

4. Mitigate
   - Apply temporary fix
   - Scale resources
   - Failover if needed

5. Communicate
   - Status page update
   - Customer notification
   - Team update

6. Resolve
   - Apply permanent fix
   - Deploy to production
   - Verify resolution

7. Post-Mortem
   - Document incident
   - Identify improvements
   - Update runbooks
```

---

## Health Check Endpoints

### Readiness Check
```bash
GET /health/ready
Response:
{
  "status": "ready",
  "database": "connected",
  "cache": "connected",
  "integrations": 3
}
```

### Liveness Check
```bash
GET /health/live
Response:
{
  "status": "alive",
  "uptime_seconds": 86400,
  "version": "1.0.0"
}
```

### Deep Health Check
```bash
GET /health/deep
Response:
{
  "database": {
    "status": "healthy",
    "latency_ms": 12,
    "connections": 15
  },
  "cache": {
    "status": "healthy",
    "hit_rate": 0.87
  },
  "integrations": {
    "office365": "syncing",
    "splunk": "healthy",
    "ad": "connected"
  }
}
```

---

## Backup & Disaster Recovery

### Backup Strategy
```
Daily:
  - Full database backup
  - Stored in separate region
  - Automated, no manual action

Weekly:
  - Full application backup
  - Configuration backup
  - Code repository backup

Monthly:
  - Disaster recovery test
  - Recovery time test
  - Documentation review
```

### Recovery Procedures
```
Database Recovery:
  1. Identify backup point
  2. Stop active connections
  3. Restore from backup
  4. Verify data integrity
  5. Resume operations

Application Recovery:
  1. Deploy from backup image
  2. Restore configuration
  3. Verify services
  4. Monitor for issues

Testing:
  - Monthly recovery drill
  - 2-hour recovery target
  - Document any issues
```

---

## Capacity Planning

### Growth Projections
```
Customers    Active Users    API Calls/min    Storage
10           500            450              50GB
50           2,500          2,250            250GB
100          5,000          4,500            500GB
200          10,000         9,000            1TB
```

### Scaling Plan
```
Up to 100 customers:
  - Current infrastructure sufficient
  - Single database fine
  - Monitor closely

100-500 customers:
  - Database read replicas
  - Cache layer expansion
  - Load balancer

500+ customers:
  - Multi-region deployment
  - Database sharding
  - CDN for frontend
  - Microservices (if needed)
```

---

## Cost Optimization

### Current Costs (Estimated)
```
AWS Staging:
  - RDS: $100/month
  - EC2: $150/month
  - S3: $20/month
  - Other: $30/month
  Total: $300/month

Monitoring:
  - Datadog: $50/month
  - Sentry: Free tier
  - ELK: Self-hosted

Total: $350/month for staging
```

### Production Estimate
```
AWS Production:
  - RDS Multi-AZ: $300/month
  - Auto-scaling EC2: $500/month
  - CloudFront CDN: $100/month
  - S3 + backups: $50/month
  - Other services: $100/month
  Total: $1,050/month

Monitoring (Production):
  - Datadog Pro: $200/month
  - PagerDuty: $100/month
  Total: $300/month

Grand Total: $1,350/month (reduces with scale)
```

---

## Monitoring ROI

### What We Monitor
✅ System availability (99.5% target)  
✅ Performance (sub-500ms target)  
✅ Data integrity (100% accurate)  
✅ Security (0 breaches target)  
✅ Customer impact (prevents churn)  

### Expected Results
- Catch issues before customers notice
- Reduce MTTR (mean time to resolution)
- Prevent data loss
- Improve reliability
- Increase customer confidence

---

**With proper monitoring, we achieve:**
- 99.5%+ uptime
- <5 minute incident response
- <15 minute resolution
- Zero silent failures
- Happy customers! 🎉
