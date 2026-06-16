
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_synthetic_data(num_users=50, days=30):
    """
    Generates synthetic user activity logs, employee database, and psychometrics.
    Injects specific insider threat patterns:
    1. Password Leakage (Type 1)
    2. Access Governance (Type 2 - Ex-employee or Role mismatch)
    """
    data_dir = 'archive(6)'
    os.makedirs(data_dir, exist_ok=True)
    
    users = [f"USR{str(i).zfill(3)}" for i in range(1, num_users + 1)]
    roles = ['IT Admin', 'HR Executive', 'Software Engineer', 'Sales Manager', 'DB Admin', 'Finance Analyst']
    departments = ['IT', 'HR', 'Engineering', 'Sales', 'Finance']
    
    # 1. Generate Employee Database
    employee_data = []
    for i, user in enumerate(users):
        status = "current"
        if i < 5: status = "ex" # First 5 are ex-employees
        
        last_working = ""
        if status == "ex":
            last_working = (datetime(2025, 12, 1) + timedelta(days=random.randint(1, 20))).strftime('%Y-%m-%d')
            
        employee_data.append({
            'employee_id': 100 + i,
            'user_id': user,
            'name': f"Employee_{user}",
            'status': status,
            'department': random.choice(departments),
            'role': random.choice(roles),
            'last_working_day': last_working
        })
    
    employee_df = pd.DataFrame(employee_data)
    employee_df.to_csv(f'{data_dir}/employee_database.csv', index=False)
    
    # 2. Generate Activity Logs (System Logs & Email-like logs)
    # Columns: user_id, timestamp, action, resource, details, ip, location, device, is_anomaly
    log_data = []
    locations = ['New York, USA', 'London, UK', 'Bangalore, India', 'San Francisco, USA', 'Berlin, Germany', 'Unknown Location']
    
    start_time = datetime(2026, 1, 1, 8, 0, 0)
    
    for user_info in employee_data:
        user = user_info['user_id']
        is_ex = user_info['status'] == "ex"
        
        # Normal users login during normal hours
        # Ex-employees should NOT login, so any login is an anomaly
        
        current_time = start_time
        for day in range(days):
            if current_time.weekday() >= 5 and random.random() < 0.8:
                current_time += timedelta(days=1)
                continue
            
            # Normal activity for current employees
            if not is_ex:
                # Daily login
                login_time = current_time + timedelta(hours=random.uniform(-1, 1))
                ip = f"192.168.1.{random.randint(10, 250)}"
                location = random.choice(locations[:-1])
                log_data.append([user, login_time.strftime('%Y-%m-%d %H:%M:%S'), 'login', 'workstation', 'Success', ip, location, 'Laptop-DELL', 0])
                
                # Daily actions
                num_actions = random.randint(5, 15)
                act_time = login_time
                for _ in range(num_actions):
                    act_time += timedelta(minutes=random.randint(15, 60))
                    action = random.choice(['file_access', 'process_exec', 'email_send'])
                    
                    if action == 'email_send':
                        log_data.append([user, act_time.strftime('%Y-%m-%d %H:%M:%S'), action, 'mail_client', 'Sent normal report', ip, location, 'Laptop-DELL', 0])
                    else:
                        log_data.append([user, act_time.strftime('%Y-%m-%d %H:%M:%S'), action, 'doc.pdf', 'Viewed', ip, location, 'Laptop-DELL', 0])
            
            current_time += timedelta(days=1)

    # 3. Inject Specific Threat Scenarios
    
    # --- Scenario A: Password-Based Insider Threat (Type 1) ---
    malicious_current = "USR010" # A current employee
    leak_time = start_time + timedelta(days=12, hours=6) # 2 PM
    ip = "192.168.1.45"
    loc = "New York, USA"
    log_data.append([malicious_current, leak_time.strftime('%Y-%m-%d %H:%M:%S'), 'email_send', 'external_mail', 'Subject: DB Access; Body: Here is the admin password: Admin@123', ip, loc, 'Laptop-DELL', 1])

    # --- Scenario B: Access Governance Threat (Type 2 - Ex-employee login) ---
    ex_user = "USR001" # An ex-employee
    bad_login_time = start_time + timedelta(days=15, hours=18) # 2 AM
    bad_ip = "49.207.12.34"
    bad_loc = "Unknown Location"
    log_data.append([ex_user, bad_login_time.strftime('%Y-%m-%d %H:%M:%S'), 'login', 'VPN', 'Success (Ex-Employee active)', bad_ip, bad_loc, 'Android-Device', 1])

    # --- Scenario C: Access Governance Threat (Type 2 - Role Mismatch / Admin Misuse) ---
    hr_user = "USR015" # HR Executive
    admin_action_time = start_time + timedelta(days=18, hours=3) # 11 AM
    log_data.append([hr_user, admin_action_time.strftime('%Y-%m-%d %H:%M:%S'), 'process_exec', 'SQL_Management_Studio', 'Attempted to modify DB roles', "192.168.1.88", "London, UK", 'Laptop-HP', 1])

    # --- Scenario D: Credential Sharing (Type 1) ---
    dev_user = "USR020"
    share_time = start_time + timedelta(days=5, hours=14) # 10 PM
    log_data.append([dev_user, share_time.strftime('%Y-%m-%d %H:%M:%S'), 'email_send', 'colleague@company.com', 'Body: Use my VPN keys attached.', "10.0.0.5", "San Francisco, USA", 'Workstation-01', 1])

    df = pd.DataFrame(log_data, columns=['user_id', 'timestamp', 'action', 'resource', 'details', 'ip', 'location', 'device', 'is_anomaly'])
    df = df.sort_values(by='timestamp').reset_index(drop=True)
    df.to_csv(f'{data_dir}/synthetic_activity.csv', index=False)
    
    # 4. Generate Psychometrics (OCEAN)
    psych_data = []
    for user in users:
        psych_data.append({
            'employee_name': f"Employee_{user}",
            'user_id': user,
            'O': random.uniform(20, 80), # Openness
            'C': random.uniform(20, 80), # Conscientiousness
            'E': random.uniform(20, 80), # Extraversion
            'A': random.uniform(20, 80), # Agreeableness
            'N': random.uniform(20, 80)  # Neuroticism
        })
    
    # Adjust anomalies to have suspicious psychometrics
    # Low C (Conscientiousness) or High N (Neuroticism) often flagged
    for p in psych_data:
        if p['user_id'] in [malicious_current, ex_user, hr_user, dev_user]:
            p['C'] = random.uniform(10, 30)
            p['N'] = random.uniform(70, 95)
            
    psych_df = pd.DataFrame(psych_data)
    psych_df.to_csv(f'{data_dir}/psychometric.csv', index=False)
    
    # Also generate a legacy email.csv for compatibility if needed
    email_data = []
    for row in log_data:
        if row[2] == 'email_send':
            email_data.append({
                'id': f"EML_{random.randint(1000, 9999)}",
                'date': row[1],
                'user': row[0],
                'pc': row[7],
                'to': row[3],
                'from': f"{row[0]}@company.com",
                'attachments': 0,
                'content': row[4]
            })
    email_df = pd.DataFrame(email_data)
    email_df.to_csv(f'{data_dir}/email.csv', index=False)

    print(f"Generated synthetic data in {data_dir}")
    return df

if __name__ == "__main__":
    generate_synthetic_data()
