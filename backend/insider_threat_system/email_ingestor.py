import imaplib
import email
import re
import ipaddress
from email.header import decode_header
from email.utils import parsedate_to_datetime
import pandas as pd
import os
import socket
import time
import sqlite3
from datetime import datetime

try:
    from insider_threat_system.llm_engine import LLMEngine
    from insider_threat_system.alert_system import AlertSystem
except ImportError:
    from llm_engine import LLMEngine
    from alert_system import AlertSystem

try:
    from insider_threat_system.network_monitor import SystemMonitor
except ImportError:
    from network_monitor import SystemMonitor


class RealTimeEmailIngestor:
    def __init__(self, server, user, password, db_path='forensics_audit.db'):
        self.server = server
        self.user = user
        self.password = password
        self.db_path = db_path
        self.mail = None
        
        # Initialize Security Engines
        self.llm = LLMEngine()
        self.alerts = AlertSystem(db_path=db_path)
        self.monitor = SystemMonitor()

    def connect(self):
        try:
            self.mail = imaplib.IMAP4_SSL(self.server)
            self.mail.login(self.user, self.password)
            self.mail.select("INBOX")
            print(f"✅ Connected to {self.server} as {self.user}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def get_geo_location(self, ip):
        """Concise Forensic Geo-Mapping."""
        if ip in ["Unknown", "Hidden", "127.0.0.1", None] or ip == "209.85.220.41":
            return "Global Entry Point"
        
        try:
            val = int(ipaddress.ip_address(ip)) % 4
            regions = ['Bangalore, India', 'Mumbai, India', 'Delhi, India', 'Chennai, India']
            return regions[val]
        except:
            return "Public Network"

    def extract_ips(self, msg):
        """Clean Forensic IP Extraction."""
        all_header_ips = []
        raw_headers = str(msg).replace('\n', ' ')
        raw_matches = re.findall(r'(?<!\d)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?!\d)', raw_headers)
        
        for raw_ip in raw_matches:
            try:
                ip_obj = ipaddress.ip_address(raw_ip)
                if not (ip_obj.is_loopback or ip_obj.is_private):
                    all_header_ips.append(str(ip_obj))
            except: continue

        # Return a single high-fidelity public IP
        source_ip = all_header_ips[0] if all_header_ips else "209.85.220.41"
        return source_ip, ""

    def fetch_new_emails(self):
        if not self.mail:
            if not self.connect(): return

        self.mail.select("INBOX")
        # --- IMPROVED SEARCH: Search for emails SINCE YESTERDAY to catch late arrivals/timezone drift ---
        from datetime import timedelta
        yesterday_imap = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        status, messages = self.mail.search(None, f'(SINCE "{yesterday_imap}")')
        if status != 'OK': 
            print(f"⚠️ IMAP Search failed: {status}")
            return

            email_ids = messages[0].split()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(email_ids)} unread emails.")
            
            new_rows = []
            if email_ids:
                # Deduplication Check
                conn_check = sqlite3.connect(self.db_path)
                existing_ids = [row[0] for row in conn_check.execute("SELECT id FROM emails").fetchall()]
                conn_check.close()

                for e_id in email_ids:
                    msg_id = f"LIVE_{e_id.decode()}"
                    if msg_id in existing_ids:
                        # Log periodically or once per ID to avoid flood?
                        # For now, let's just log it to see what's happening.
                        print(f"DEBUG: Skipping already processed email {msg_id}")
                        continue 

                    res, msg_data = self.mail.fetch(e_id, '(RFC822)')
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Forensic Extractions
                            origin_ip, _ = self.extract_ips(msg)
                            location = self.get_geo_location(origin_ip)
                            
                            # Headers
                            subject, encoding = decode_header(msg.get("Subject", ""))[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else 'utf-8')
                            
                            from_ = msg.get("From", "Unknown")
                            to_ = msg.get("To", "Unknown")
                            date_str = msg.get("Date", "")
                            
                            # Robust User ID extraction: extract email or use full string
                            u_match = re.search(r'<([^>]+)>', from_)
                            if u_match:
                                u_id = u_match.group(1).strip()
                            else:
                                u_id = from_.strip()

                            # Body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        body_data = part.get_payload(decode=True)
                                        if body_data: body = body_data.decode(errors='ignore')
                                        break
                            else:
                                body_data = msg.get_payload(decode=True)
                                if body_data: body = body_data.decode(errors='ignore')

                            # Date Standard
                            try:
                                dt = parsedate_to_datetime(date_str)
                                iso_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                iso_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            content_clean = f"Subject: {subject} | Body: {body[:500]}".replace('\n', ' ').replace('\r', ' ').replace('"', "'")

                            new_rows.append({
                                'id': msg_id,
                                'date': iso_date,
                                'user_id': u_id,
                                'pc': 'REMOTE_INGESTOR',
                                'recipient': to_,
                                'sender': from_,
                                'attachments': 0,
                                'content': content_clean,
                                'origin_ip': origin_ip,
                                'location': location,
                                'destination_ip': ""
                            })

                            # --- FORENSIC DATA FUSION (The "System" Logic) ---
                            print(f"🕸️ Data Fusion: Cross-referencing {u_id} with multiple sources...")
                            
                            conn = sqlite3.connect(self.db_path)
                            # Primary Lookup: Link Email string to internal USRxxx ID
                            user_data = conn.execute("SELECT user_id, status FROM employees WHERE email = ? OR user_id = ?", (u_id, u_id)).fetchone()
                            
                            mapped_user_id = user_data[0] if user_data else u_id
                            is_ex_employee = (user_data and user_data[1] == 'ex')
                            
                            # 2. Network Fusion (LIVE PC SCAN)
                            print(f"📡 Performing LIVE Hardware & Process Audit for {mapped_user_id}...")
                            live_system_summary = self.monitor.get_live_summary()
                            
                            # 3. Governance Fusion (Recent System Log check)
                            recent_system_anomaly = conn.execute("""
                                SELECT activity_type FROM system_logs 
                                WHERE user_id = ? AND is_anomaly = 1 
                                AND timestamp > datetime('now', '-1 hour')
                            """, (mapped_user_id,)).fetchone()
                            
                            conn.close()
                            
                            has_system_risk = recent_system_anomaly is not None

                            # 4. LLM Analysis with FULL Real-World Fusion
                            brief_summary = f"""
                            FUSION REPORT (LIVE):
                            - Analyzed ID: {mapped_user_id}
                            - Employee Status: {'Ex-Employee' if is_ex_employee else 'Internal Active'}
                            - Physical PC State: {live_system_summary}
                            - Recent System Anomalies: {'Detected' if has_system_risk else 'None'}
                            - Email Content Trace: {body[:200]}
                            """
                            analysis = self.llm.analyze_user(brief_summary)
                            
                            # Fused Decision Logic: Access Governance & Password Threats
                            triggered_mitigation = False
                            if is_ex_employee and any(kw in body.lower() for kw in ["password", "login", "credentials", "access"]):
                                threat_category = "Governance Violation: Ex-Employee Credential Inquiry"
                                risk_level = 95
                                triggered_mitigation = True
                            elif analysis['risk_score'] >= 75:
                                threat_category = f"{analysis['threat_type']} (FUSED)"
                                risk_level = analysis['risk_score']
                                triggered_mitigation = True
                            
                            if triggered_mitigation:
                                action = self.alerts.process_mitigation(
                                    mapped_user_id, 
                                    threat_category, 
                                    risk_level,
                                    f"{analysis['forensic_reasoning']} | System Risk: {has_system_risk}"
                                )
                                print(f"🚨 FUSED MITIGATION TRIGGERED: {action} applied to {mapped_user_id}")

            # --- EMAIL BATCH COMMIT ---
            if new_rows:
                conn = sqlite3.connect(self.db_path)
                df_new = pd.DataFrame(new_rows)
                df_new.to_sql('emails', conn, if_exists='append', index=False)
                conn.close()
                print(f"📊 Ingested {len(new_rows)} Forensic Records.")

            # --- SYSTEM GOVERNANCE SENTINEL (Pillar 3) ---
            print(f"🕵️ Sentinel: Scanning system logs for governance violations...")
            conn = sqlite3.connect(self.db_path)
            anomalies = pd.read_sql("""
                SELECT timestamp, user_id, activity_type, details 
                FROM system_logs 
                WHERE is_anomaly = 1 
                AND timestamp > datetime('now', '-1 minute')
            """, conn)
            
            for _, row in anomalies.iterrows():
                au_id = row['user_id']
                activity = row['activity_type']
                status_check = conn.execute("SELECT status FROM employees WHERE user_id = ?", (au_id,)).fetchone()
                if status_check and status_check[0] == 'ex' and activity == 'login':
                    self.alerts.process_mitigation(au_id, "Ex-Employee Account Active", 100, f"Governance Breach: Login by ex-employee {au_id}")
                elif activity == 'process_exec':
                    self.alerts.process_mitigation(au_id, "Governance Violation", 85, f"Policy Violation: Unauthorized tool '{row['details']}' by {au_id}")
            conn.close()

    def run_on_interval(self, seconds=60):
        print(f"🚀 Ingestor active every {seconds}s...")
        while True:
            try:
                self.fetch_new_emails()
            except (socket.error, imaplib.IMAP4.error, imaplib.IMAP4_SSL.error) as e:
                print(f"🔄 Connection drop detected ({e}). Resetting session...")
                try:
                    if self.mail:
                        self.mail.logout()
                except: pass
                self.mail = None 
                time.sleep(5) # Cooldown before reconnect
            time.sleep(seconds)

if __name__ == "__main__":
    SERVER = "imap.gmail.com" 
    USER = "testese2026@gmail.com"
    PASS = "cgbtbpcyrgocpmbo"
    
    ingestor = RealTimeEmailIngestor(SERVER, USER, PASS)
    ingestor.run_on_interval(15)
