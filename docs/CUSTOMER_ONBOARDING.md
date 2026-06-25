# 🎓 CUSTOMER ONBOARDING GUIDE

## Welcome to InsiderThreat-AI Beta! 👋

Thank you for joining our beta program. This guide will help you get started in 30 minutes.

---

## Step 1: Account Setup (5 minutes)

### Access Your Account
```
URL: https://beta.insiderthreat-ai.com
Email: [your-company@example.com]
Password: [Your temporary password]
```

### First Login
1. Navigate to login page
2. Enter your credentials
3. Set up two-factor authentication (2FA)
4. Create your security questions

### Profile Setup
1. Go to Settings > Profile
2. Add your full name
3. Set your timezone
4. Enable notification preferences

---

## Step 2: Organization Setup (10 minutes)

### Invite Team Members
```
Settings > Team Members > Invite

Add:
- Security Officer (viewing access)
- SOC Analyst (operational access)
- Auditor (read-only access)
```

### Configure Organization
```
Settings > Organization

- Set data retention (90, 180, 365 days)
- Enable audit logging
- Configure report recipients
- Set threat thresholds
```

---

## Step 3: Integration Setup (15 minutes)

### Connect Your Data Sources

#### Option 1: Office365
```
Settings > Integrations > Add Integration

Type: Office365
Steps:
1. Register OAuth app in Azure Portal
2. Copy Client ID & Secret
3. Paste in our settings
4. Click "Test Connection"
5. Grant permissions when prompted
```

#### Option 2: Splunk
```
Settings > Integrations > Add Integration

Type: Splunk
Steps:
1. Get Splunk host URL
2. Create API user with search permissions
3. Enter credentials
4. Click "Test Connection"
5. Configure search queries (optional)
```

#### Option 3: Active Directory
```
Settings > Integrations > Add Integration

Type: Active Directory
Steps:
1. Provide AD server hostname
2. Create service account (read-only)
3. Enter credentials
4. Click "Test Connection"
5. Map attributes (optional)
```

### Verify Integration
```
After setup:
1. Check "Last Sync" timestamp
2. Review "Activity Log" for events
3. Go to Dashboard to see live data
```

---

## Step 4: Exploring the Platform

### Dashboard Overview
```
Home > Dashboard

Shows:
- Total Assessments: Users analyzed
- Flagged Threats: High-risk employees
- Average Risk Score: Overall risk
- Monitored Employees: Total user base

Charts:
- Risk Trend: 7-day history
- Threat Distribution: Normal/Negligent/Suspicious/Malicious
- Recent Threats: Latest detections
```

### Threat Management
```
Threats > All Threats

Features:
- Search by employee ID
- Filter by threat type
- Sort by risk score
- Click for details

Actions:
- Acknowledge threat
- View timeline
- See MITRE mapping
- Download evidence
```

### Generate Reports
```
Reports > Generate Report

Options:
- Report Type: Daily/Weekly/Monthly/Custom
- Time Period: Last 7/30/90 days
- Include Charts: Yes/No
- Distribution: Download/Email

View Reports:
- Download as PDF
- Email to team
- Schedule recurring
```

### Analytics
```
Analytics > Insights

View:
- Threat trends over time
- Risk by department
- Event volume trends
- Integration health
```

---

## Common Questions

### Q: How does threat detection work?
A: We combine:
1. **ML Analysis**: Isolation Forest detects statistical anomalies
2. **LLM Context**: GPT-4 adds human-like reasoning
3. **Rule Engine**: Custom rules for your organization
4. **Integration Data**: Email, SIEM, AD, cloud logs

### Q: What data is collected?
A: We collect:
- Employee ID, name, department
- Login activities, file access
- Email metadata (not content)
- Network connections
- System events

### Q: How is data secured?
A: We provide:
- AES-256 encryption at rest
- TLS 1.3 for all traffic
- Audit logging of all access
- GDPR/HIPAA compliance
- Data retention policies

### Q: Can I export my data?
A: Yes! You can:
- Export reports as PDF
- Download threat data as CSV
- Access via REST API
- Schedule automated exports

### Q: What if I need help?
A: Contact us via:
- Slack: #beta-support (dedicated channel)
- Email: support@insiderthreat-ai.com
- Phone: Available for critical issues

---

## Feature Walkthrough Videos

### Dashboard Overview (5 min)
```
Watch here: https://beta.insiderthreat-ai.com/videos/dashboard

Learn:
- Dashboard metrics
- Interactive charts
- Real-time updates
- Customization options
```

### Threat Investigation (7 min)
```
Watch here: https://beta.insiderthreat-ai.com/videos/threats

Learn:
- Search & filtering
- Threat details view
- Timeline visualization
- Evidence review
```

### Integration Setup (8 min)
```
Watch here: https://beta.insiderthreat-ai.com/videos/integrations

Learn:
- Step-by-step setup
- Testing connections
- Troubleshooting common issues
- Webhook configuration
```

### Report Generation (5 min)
```
Watch here: https://beta.insiderthreat-ai.com/videos/reports

Learn:
- Report types
- Customization options
- Scheduling reports
- Distribution methods
```

---

## Quick Reference

### Keyboard Shortcuts
```
? = Help menu
/ = Search
c = Create new
e = Edit
d = Delete (careful!)
```

### Admin Controls
```
Only available to Admin role:
- User management
- Integration configuration
- Organization settings
- API key generation
- Billing configuration
```

### SOC Analyst Controls
```
Available to SOC Analyst role:
- View all threats
- Acknowledge threats
- Generate reports
- View integrations (read-only)
```

### Auditor Controls
```
Available to Auditor role (read-only):
- View all threats
- View reports
- View audit logs
- View configurations
```

---

## Troubleshooting

### Integration Not Syncing
```
Step 1: Check credentials
  Settings > Integrations > [Integration] > Edit
  Verify username/password/API key

Step 2: Test connection
  Click "Test Connection" button
  Check for error messages

Step 3: Review logs
  Check "Last Sync" time
  Look for error messages
  
Step 4: Contact support
  If issues persist, contact us with:
  - Integration type
  - Error message
  - When it stopped working
```

### Slow Dashboard
```
Step 1: Clear browser cache
  Ctrl+Shift+Delete (Chrome)
  Cmd+Shift+Delete (Safari)

Step 2: Check internet connection
  Run speed test: speedtest.net
  Switch to 4G/WiFi if slow

Step 3: Try different browser
  Chrome, Firefox, Safari all supported

Step 4: Contact support
  If still slow, collect:
  - Browser & version
  - Network latency
  - Dashboard load time
```

### Login Issues
```
Step 1: Check email address
  Verify correct email
  Check for typos

Step 2: Reset password
  Click "Forgot Password"
  Follow email instructions

Step 3: Check 2FA
  If 2FA enabled, have your device ready
  Check authenticator app

Step 4: Contact support
  Email: support@insiderthreat-ai.com
```

---

## Support Resources

### Documentation
- Full API Reference: https://docs.insiderthreat-ai.com/api
- Integration Guides: https://docs.insiderthreat-ai.com/integrations
- Security Policy: https://insiderthreat-ai.com/security
- Privacy Policy: https://insiderthreat-ai.com/privacy

### Contact
- Slack: #beta-support
- Email: beta@insiderthreat-ai.com
- Phone: +1-555-THREAT-AI (emergency only)

### Community
- Forum: https://community.insiderthreat-ai.com
- GitHub: https://github.com/insiderthreat-ai
- Twitter: @InsiderThreatAI

---

## Next Steps

### This Week
- [ ] Set up your account
- [ ] Invite team members
- [ ] Connect your first integration
- [ ] Explore dashboard
- [ ] Run sample report

### Next Week
- [ ] Connect all data sources
- [ ] Configure custom rules
- [ ] Schedule weekly reports
- [ ] Set up team alerts
- [ ] Review first threats

### Feedback
```
We'd love to hear from you!

Report Issues:
- Slack: Quick messages
- Email: Detailed reports
- Issue tracker: Feature requests

Daily Feedback Call:
- Monday 10am EST
- 30 minutes per customer
- Review what's working/not
- Discuss priorities
```

---

## Beta Expectations

### What to Expect
✅ Regular updates (daily/weekly)  
✅ Quick bug fixes (<24 hours)  
✅ Responsive support (during business hours)  
✅ Feature additions based on feedback  

### What NOT to Expect
❌ 100% uptime (99.5% target)  
❌ Zero bugs (rapid iteration environment)  
❌ 24/7 on-call support  
❌ SLA guarantees (beta only)  

### Timeline
- Beta Period: 2 weeks
- Feedback Loop: Daily
- GA Release: Week 9+
- Pricing: TBD after beta

---

## Thank You! 🙏

Thank you for participating in our beta program. Your feedback is critical to our success!

Together, we're building the future of insider threat detection.

Questions? Reach out anytime! 🚀

---

**Welcome to InsiderThreat-AI Beta!**
