
import pandas as pd

def summarize_user_activity(email_df, psychometrics, user_id, user_ml_stats=None, synthetic_df=None, employee_info=None):
    """
    Creates a natural language summary of the user's activity, psychometric profile, and employee status.
    Incorporates Machine Learning features and system logs if provided.
    """
    user_emails = email_df[email_df['user'] == user_id] if email_df is not None else pd.DataFrame()
    
    # 1. Employee Context
    emp_context = ""
    if employee_info:
        emp_context = (
            f"- Status: {employee_info.get('status', 'Unknown')}\n"
            f"- Role: {employee_info.get('role', 'Unknown')}\n"
            f"- Department: {employee_info.get('department', 'Unknown')}\n"
        )
        if employee_info.get('status') == 'ex':
            emp_context += f"- Last Working Day: {employee_info.get('last_working_day', 'N/A')}\n"
    
    # 2. Email Stats & Forensic Metadata
    total_emails = len(user_emails)
    flagged_emails = 0
    suspicious_keywords = [
        'password', 'admin', 'root', 'secret', 'vpn', 'credentials', 
        'keys', 'token', 'login', 'pass:', 'user:', 'private'
    ]
    
    email_summary_bits = []
    latest_forensics = ""
    for _, row in user_emails.iterrows():
        content = str(row.get('content', '')).lower()
        if any(w in content for w in suspicious_keywords):
            flagged_emails += 1
            email_summary_bits.append(f"Email Content: '{row.get('content')[:100]}...'")
            # Capture forensics from the latest suspicious email
            if not latest_forensics:
                latest_forensics = (
                    f"- Recent Message Origin: {row.get('location', 'N/A')}\n"
                    f"- Sender IP: {row.get('origin_ip', 'N/A')}\n"
                    f"- Receiver Server IP: {row.get('destination_ip', 'N/A')}\n"
                )

    # 3. System Logs (Synthetic)
    log_text = latest_forensics # Pre-populate with email forensics if available
    if synthetic_df is not None and not synthetic_df.empty:
        user_logs = synthetic_df[synthetic_df['user_id'] == user_id]
        if not user_logs.empty:
            # Get the most recent or anomalous log entry
            latest_log = user_logs.iloc[-1]
            log_text += f"- Login Time: {latest_log['timestamp'].strftime('%Y-%m-%d %I:%M %p')}\n"
            log_text += f"- IP: {latest_log.get('ip', 'N/A')}\n"
            log_text += f"- Location: {latest_log.get('location', 'N/A')}\n"
            log_text += f"- Device: {latest_log.get('device', 'N/A')}\n"
            
            # Anomalous actions
            anomaly_logs = user_logs[user_logs['is_anomaly'] == 1]
            if not anomaly_logs.empty:
                for _, alog in anomaly_logs.iterrows():
                    log_text += f"- Suspicious Action: {alog['activity']} ({alog['details']})\n"
                    
    if not log_text:
        log_text = "- No system logs available.\n"

    # 4. Psychometrics
    psycho_text = "Unknown"
    if psychometrics:
        psycho_text = (
            f"O={psychometrics.get('O')}, C={psychometrics.get('C')}, "
            f"N={psychometrics.get('N')} (Low Conscientiousness/High Neuroticism indicates risk)"
        )
    
    # 5. Machine Learning Context
    ml_context = ""
    if user_ml_stats:
        ml_score = user_ml_stats.get('ml_risk_score', 0)
        ml_context = f"- ML Baseline Anomaly Score: {ml_score:.2f}/100\n"

    # Construct Final Narrative
    summary = f"""
Insider Threat Diagnostic Context:
{emp_context}
System Activity Logs:
{log_text.strip()}

Messaging Activity:
- Total emails: {total_emails}
- Suspicious Email Count: {flagged_emails}
{chr(10).join(email_summary_bits[:2])}

{ml_context}
User Psychology Profile:
{psycho_text}
    """
    
    return summary.strip()
