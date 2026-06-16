
import sqlite3
import pandas as pd
import time
import random
import os
from datetime import datetime

DB_PATH = 'forensics_audit.db'

def simulate_live_activity():
    if not os.path.exists(DB_PATH):
        print("Error: Database forensics_audit.db not found. Run db_init.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    employees = pd.read_sql("SELECT user_id, status FROM employees", conn)
    current_users = employees[employees['status'] == 'current']['user_id'].tolist()
    ex_users = employees[employees['status'] == 'ex']['user_id'].tolist()
    conn.close()

    actions = ['login', 'file_access', 'process_exec', 'email_send']
    locations = ['New York, USA', 'London, UK', 'Bangalore, India', 'San Francisco, USA', 'Berlin, Germany']
    
    print("🚀 ThreatSentinel SQL-Live Simulator Started...")
    print("Press Ctrl+C to stop simulation.")

    while True:
        try:
            is_threat = random.random() < 0.15
            new_logs = []
            
            if is_threat:
                scenario = random.choice(['password_leak', 'ex_employee', 'role_mismatch'])
                
                if scenario == 'password_leak':
                    user = random.choice(current_users)
                    details = random.choice([
                        "Subject: Password for root; Body: Admin123",
                        "Body: Here are the VPN keys for the prod server.",
                        "Subject: Credentials; Body: Shared via unencrypted mail"
                    ])
                    new_logs.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'user_id': user, 
                        'pc': 'Laptop-DELL',
                        'activity_type': 'email_send',
                        'details': details,
                        'is_anomaly': 1
                    })
                    print(f"🔴 [THREAT INJECTED] Password Leak by {user}")

                elif scenario == 'ex_employee':
                    user = random.choice(ex_users)
                    new_logs.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'user_id': user, 
                        'pc': 'Anonymous-Device',
                        'activity_type': 'login',
                        'details': "Success (Ex-Employee account login bypass)",
                        'is_anomaly': 1
                    })
                    print(f"🔴 [THREAT INJECTED] Ex-Employee Login: {user}")

                elif scenario == 'role_mismatch':
                    user = random.choice(current_users)
                    new_logs.append({
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'user_id': user, 
                        'pc': 'Workstation-05',
                        'activity_type': 'process_exec',
                        'details': "Attempted to stop DB services",
                        'is_anomaly': 1
                    })
                    print(f"🟠 [THREAT INJECTED] Role Mismatch by {user}")
            
            else:
                user = random.choice(current_users)
                action = random.choice(actions)
                details = "Viewed project docs" if action == 'file_access' else "System idle"
                new_logs.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'user_id': user, 
                    'pc': 'Company-Laptop',
                    'activity_type': action,
                    'details': details,
                    'is_anomaly': 0
                })
                print(f"🟢 [NORMAL] Activity logged for {user}")

            if new_logs:
                conn = sqlite3.connect(DB_PATH)
                pd.DataFrame(new_logs).to_sql('system_logs', conn, if_exists='append', index=False)
                conn.close()
            
            time.sleep(random.randint(10, 15))
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Sim error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    simulate_live_activity()
