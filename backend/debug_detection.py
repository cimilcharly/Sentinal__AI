
import pandas as pd
import os
import sys

# Ensure local modules can be imported
sys.path.append(os.getcwd())

from insider_threat_system.data_loader import load_emails, load_employees_db, get_employee_info
from insider_threat_system.summarizer import summarize_user_activity
from insider_threat_system.llm_engine import LLMEngine

email_path = 'archive(6)/email.csv'
emp_path = 'archive(6)/employee_database.csv'

emails = load_emails(email_path, sample_size=5000)
employees = load_employees_db(emp_path)

print(f"Total emails loaded: {len(emails)}")

# Find ANY user with an email in the "Leakage Monitor"
leak_keywords = 'password|admin|vpn|keys|root|credentials|secret'
suspicious_emails = emails[emails['content'].str.contains(leak_keywords, case=False, na=False)]
live_leakers = suspicious_emails['user'].unique() if emails is not None else []

print(f"Suspicious emails found: {len(suspicious_emails)}")
print(f"Unique leakers identified: {live_leakers}")

if len(live_leakers) > 0:
    user = live_leakers[-1] # Try the last one
    print(f"\n--- Testing User: {user} ---")
    
    emp_info = get_employee_info(employees, user)
    if emp_info is None:
        print("User not found in employee DB. Using GUEST default.")
        emp_info = {'status': 'guest', 'role': 'External User', 'department': 'Remote'}
    
    user_ml_stats = {'ml_risk_score': 90.0} # Default for leaker
    
    # We pass None for psychs and synthetic for this simple test
    summary = summarize_user_activity(emails, None, user, user_ml_stats, None, emp_info)
    print("\n[SUMMARY GENERATED]")
    print(summary)
    
    engine = LLMEngine(use_mock=True)
    analysis = engine.analyze_user(summary)
    print("\n[AI ANALYSIS]")
    import json
    print(json.dumps(analysis, indent=2))
else:
    print("No leakers found in the current sample.")
