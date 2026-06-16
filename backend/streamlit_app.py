import streamlit as st
import pandas as pd
import sys
import os
import socket
import datetime
import time
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Ensure local modules can be imported
sys.path.append(os.getcwd())

from insider_threat_system.data_loader import (
    load_emails, load_psychometrics, get_user_psychometrics, 
    load_synthetic_activity, load_employees_db, get_employee_info,
    load_mitigation_logs
)
from insider_threat_system.summarizer import summarize_user_activity
from insider_threat_system.llm_engine import LLMEngine
from insider_threat_system.ml_engine import MLRiskEngine
from insider_threat_system.network_monitor import SystemMonitor
from insider_threat_system.auth import init_auth_config, CONFIG_PATH

# --- Authentication Gateway Setup ---
init_auth_config()
with open(CONFIG_PATH, 'r') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize Streamlit Authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Render standard login interface
try:
    authenticator.login()
except TypeError:
    authenticator.login('Login', 'main')

# Handle authentication states
if st.session_state.get("authentication_status") == False:
    st.error('Username/password is incorrect')
elif st.session_state.get("authentication_status") == None:
    st.warning('Please login with your corporate credentials.')
    st.info("💡 Default Accounts:\n- Admin: admin / admin123\n- Analyst: analyst / analyst123")
else:
    # Authenticated block
    username = st.session_state["username"]
    user_role = config['credentials']['usernames'][username].get('role', 'analyst')

    # --- Page Config ---
    st.set_page_config(
        page_title="ThreatSentinel | Live Detection",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Premium CSS ---
    st.markdown("""
    <style>
        .stApp { background-color: #0d1117; color: #c9d1d9; }
        section[data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
        .dashboard-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; background: #161b22; border-bottom: 2px solid #30363d; border-radius: 10px; margin-bottom: 25px; }
        .metric-card { background: rgba(22, 27, 34, 0.8); border: 1px solid #30363d; border-radius: 12px; padding: 20px; text-align: center; transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-5px); border-color: #58a6ff; }
        .explanation-card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 25px; margin-bottom: 20px; }
        .risk-gauge { font-size: 2.5rem; font-weight: bold; color: #ff7b72; text-shadow: 0 0 10px rgba(255, 123, 114, 0.3); }
        .behavioral-flag { display: inline-block; padding: 4px 12px; border-radius: 20px; background: rgba(88, 166, 255, 0.1); border: 1px solid #58a6ff; color: #58a6ff; font-size: 0.8rem; margin-right: 10px; margin-bottom: 10px; }
        .behavioral-flag.critical { background: rgba(255, 123, 114, 0.1); border-color: #ff7b72; color: #ff7b72; }
        .status-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
        .status-online { background-color: #238636; }
        .status-alert { background-color: #da3633; box-shadow: 0 0 8px #da3633; }
        .stButton > button { width: 100%; text-align: left; background-color: transparent; border: none; color: #c9d1d9; padding: 10px 5px; border-radius: 5px; }
        .stButton > button:hover { background-color: #30363d; color: #58a6ff; }
        .live-badge { background: #238636; color: white; padding: 2px 7px; border-radius: 4px; font-size: 0.6rem; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = "Threat Dashboard"

    # --- Data Loading ---
    def load_all_data_live(sample_size):
        emails = load_emails(sample_size=sample_size)
        psychs = load_psychometrics()
        synthetic = load_synthetic_activity()
        employees = load_employees_db()
        mitigations = load_mitigation_logs()
        return emails, psychs, synthetic, employees, mitigations

    # --- SIDEBAR & AUTH STATS ---
    with st.sidebar:
        st.markdown("<h1 style='color:#58a6ff;'>⚡ ThreatSentinel</h1>", unsafe_allow_html=True)
        st.write(f"Logged in as: **{st.session_state['name']}**")
        st.write(f"Clearance: `{user_role.upper()}`")
        authenticator.logout('Sign Out', 'sidebar')
        st.divider()
        
        st.subheader("Navigation")
        if st.button("🏠 Threat Dashboard"): st.session_state.active_tab = "Threat Dashboard"
        if st.button("📧 Email Monitor"): st.session_state.active_tab = "Email Monitor"
        if st.button("👤 User Activity"): st.session_state.active_tab = "User Activity"
        if st.button("📊 Threat Explanation"): st.session_state.active_tab = "Threat Explanation"
        if st.button("🔓 Ex-Employee Watch"): st.session_state.active_tab = "Ex-Employee Watch"
        
        # Admin restricted pages
        if user_role == "admin":
            if st.button("🛡️ Mitigation Hub"): st.session_state.active_tab = "Mitigation Hub"
            if st.button("🌐 Live Host Audit"): st.session_state.active_tab = "Live System Audit"
        
        st.divider()
        st.subheader("Live Controls")
        auto_refresh = st.checkbox("Auto-Refresh Dashboard", value=False)
        sample_size = st.slider("Log Sample Size", 1000, 100000, 50000)
        if st.button("🔄 Force Refresh"): st.rerun()

    # Protect administrative routes from unauthorized role escalation
    if st.session_state.active_tab in ["Mitigation Hub", "Live System Audit"] and user_role != "admin":
        st.session_state.active_tab = "Threat Dashboard"
        st.error("🚫 Access Denied: You do not have the required administrative clearance to view this module.")

    # --- REFRESH LOGIC ---
    if auto_refresh:
        time.sleep(10)
        st.rerun()

    # --- GLOBAL DATA PREP ---
    emails, psychs, synthetic, employees, mitigations = load_all_data_live(sample_size)
    ml_engine = MLRiskEngine()
    ml_features_df = ml_engine.train_and_score(emails, psychs, synthetic) if emails is not None else pd.DataFrame()

    # --- DASHBOARD HEADER ---
    st.markdown(f"""
    <div class="dashboard-header">
        <div style="display:flex; gap:30px; align-items:center;">
            <div><span class="status-dot status-alert"></span><span style="color:#ff7b72; font-weight:bold;">{len(synthetic[synthetic['is_anomaly']==1]) if not synthetic.empty else 0} ANOMALIES</span></div>
            <div><span class="status-dot status-online"></span><span style="color:#3fb950; font-weight:bold;">{len(employees)} MONITORED</span></div>
        </div>
        <div style="display:flex; gap:20px; align-items:center;">
            <span class="live-badge">LIVE ENGINE</span>
            <div style="color:#8b949e; font-size:0.9rem;">SYNC: {datetime.datetime.now().strftime('%H:%M:%S')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- PAGE ROUTING ---

    if st.session_state.active_tab == "Threat Dashboard":
        col_main, col_feed = st.columns([3, 1])

        with col_main:
            # Card counts based on REAL data
            num_leaks = len(synthetic[synthetic['details'].str.contains('password|Root@', na=False)]) if not synthetic.empty else 0
            gov_viol = len(synthetic[(synthetic['is_anomaly']==1) & (~synthetic['details'].str.contains('password|Root@', na=False))]) if not synthetic.empty else 0
            
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="metric-card"><p style="color:#8b949e; font-size:0.8rem;">TOTAL LOGS</p><h1 style="color:#58a6ff; margin:0;">{len(synthetic) if not synthetic.empty else 0}</h1></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-card"><p style="color:#8b949e; font-size:0.8rem;">CREDENTIAL LEAKS</p><h1 style="color:#ff7b72; margin:0;">{num_leaks}</h1></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-card"><p style="color:#8b949e; font-size:0.8rem;">GOV. VIOLATIONS</p><h1 style="color:#ffa657; margin:0;">{gov_viol}</h1></div>', unsafe_allow_html=True)
            locked_count = len(employees[employees['status']=='LOCKED']) if not employees.empty else 0
            with c4: st.markdown(f'<div class="metric-card"><p style="color:#8b949e; font-size:0.8rem;">LOCKED ACCOUNTS</p><h1 style="color:#ff4b4b; margin:0;">{locked_count}</h1></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("// Active Hybrid Risk Assessment")
            
            # Combine ML-ranked users with "Live" suspicious email users
            ml_risky = ml_features_df.sort_values(by='ml_risk_score', ascending=False)['user_id'].unique()[:10] if not ml_features_df.empty else []
            
            # Find ANY user with an email in the "Leakage Monitor"
            leak_keywords = 'password|admin|vpn|keys|root|credentials|secret'
            live_leakers = emails[emails['content'].str.contains(leak_keywords, case=False, na=False)]['user'].unique() if emails is not None else []
            
            # Merge lists
            all_risky = list(dict.fromkeys(list(live_leakers) + list(ml_risky)))[:15]

            if all_risky:
                engine = LLMEngine(use_mock=True)
                table_data = []
                for user in all_risky:
                    emp_info = get_employee_info(employees, user)
                    if emp_info is None:
                        emp_info = {'status': 'guest', 'role': 'External User', 'department': 'Remote'}
                    
                    real_name = emp_info.get('employee_name', user)
                    
                    # Get ML stats
                    user_ml_rows = ml_features_df[ml_features_df['user_id'] == user]
                    if not user_ml_rows.empty:
                        user_ml_stats = user_ml_rows.iloc[0].to_dict()
                    else:
                        has_leak = user in live_leakers
                        user_ml_stats = {'ml_risk_score': 90.0 if has_leak else 10.0}

                    summary = summarize_user_activity(emails, get_user_psychometrics(psychs, user), user, user_ml_stats, synthetic, emp_info)
                    
                    # Analyze user with PII masking support
                    analysis = engine.analyze_user(summary, user_id=user, real_name=real_name)
                    
                    table_data.append({
                        "USER": user, "STATUS": emp_info.get('status', 'current').upper(),
                        "THREAT": analysis.get('threat_type', 'No Threat'),
                        "ML RISK": round(user_ml_stats['ml_risk_score'], 1),
                        "ACTION": analysis.get('governance_action', 'Log'),
                        "STATUS_RAW": emp_info.get('status', 'current')
                    })
                df = pd.DataFrame(table_data)
                def style_row(row):
                    stls = [''] * len(row)
                    if row['THREAT'] != 'No Threat': stls[2] = 'color: #ff7b72; font-weight: bold;'
                    if row['STATUS_RAW'] == 'ex': stls[1] = 'color: #ff4b4b; font-weight: bold;'
                    return stls
                st.dataframe(df.style.apply(style_row, axis=1), use_container_width=True, column_config={"ML RISK": st.column_config.ProgressColumn(min_value=0, max_value=100), "STATUS_RAW": None})

        with col_feed:
            st.markdown('<h4 style="color:#58a6ff; margin-bottom:15px;">🔔 LIVE FEED</h4>', unsafe_allow_html=True)
            if not synthetic.empty:
                latest_anomalies = synthetic[synthetic['is_anomaly'] == 1].sort_values(by='timestamp', ascending=False).head(10)
                for _, alert in latest_anomalies.iterrows():
                    color = "#ff7b72" if "password" in alert['details'].lower() or alert['user_id'] in employees[employees['status']=='ex']['user_id'].values else "#ffa657"
                    st.markdown(f"""
                    <div style="border-left: 3px solid {color}; padding-left: 10px; margin-bottom: 15px; background: rgba(255,255,255,0.05); padding-top:5px; padding-bottom:5px; border-radius: 0 5px 5px 0;">
                        <p style="font-size:0.75rem; color:{color}; font-weight:bold; margin:0;">{alert['activity'].upper()}</p>
                        <p style="font-size:0.7rem; color:#8b949e; margin:0;">{alert['timestamp'].strftime('%I:%M:%S %p')} | {alert['user_id']}</p>
                        <p style="font-size:0.75rem; margin-top:3px;">{alert['details'][:60]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("Awaiting live data stream...")

    elif st.session_state.active_tab == "Email Monitor":
        st.header("📧 Email Forensics Hub")
        
        tab1, tab2 = st.tabs(["🚨 Malicious Detections", "📜 Full Forensic Log"])
        
        with tab1:
            if emails is not None:
                leak_keywords = 'password|admin|vpn|keys|root|credentials|secret|token|login|hack'
                suspicious = emails[emails['content'].str.contains(leak_keywords, case=False, na=False)]
                
                def get_severity(text):
                    low_text = text.lower()
                    if any(w in low_text for w in ['password', 'admin', 'vpn', 'secret', 'credentials', 'hack']):
                        return "🚨 CRITICAL"
                    return "⚠️ SUSPICIOUS"
                
                if not suspicious.empty:
                    suspicious = suspicious.copy()
                    suspicious['SEVERITY'] = suspicious['content'].apply(get_severity)
                    suspicious = suspicious.sort_values(by='date', ascending=False, na_position='last')
                    
                    st.dataframe(
                        suspicious[['SEVERITY', 'date', 'user', 'to', 'content']],
                        column_config={"content": st.column_config.TextColumn("Filtered Content", width="large")},
                        hide_index=True,
                        use_container_width=True
                    )
                    st.warning(f"Found {len(suspicious)} records matching threat signatures.")
                else:
                    st.success("✅ No malicious email signatures detected in the current sample.")

        with tab2:
            if emails is not None:
                st.subheader("Real-Time Ingestion Log")
                full_log = emails.sort_values(by='date', ascending=False)
                display_cols = ['date', 'user', 'location', 'to', 'content']
                st.dataframe(
                    full_log[display_cols],
                    column_config={
                        "date": "Time",
                        "user": "Sender",
                        "location": "Origin",
                        "content": st.column_config.TextColumn("Raw Body", width="large")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                st.info(f"Displaying all {len(full_log)} captured records from the forensic stream.")

    elif st.session_state.active_tab == "User Activity":
        st.header("👤 User Forensics")
        selected_user = st.selectbox("Select User ID:", employees['user_id'].unique())
        user_logs = synthetic[synthetic['user_id'] == selected_user].sort_values(by='timestamp', ascending=False)
        st.dataframe(user_logs, use_container_width=True)

    elif st.session_state.active_tab == "Ex-Employee Watch":
        st.header("🔓 Inactive Account Monitor")
        ex_ids = employees[employees['status'] == 'ex']['user_id'].values
        violations = synthetic[synthetic['user_id'].isin(ex_ids)].sort_values(by='timestamp', ascending=False)
        if not violations.empty:
            st.error(f"ALERT: {len(violations)} security events involving ex-employees.")
            st.dataframe(violations, use_container_width=True)
        else:
            st.success("Governance Check: No ex-employee activity.")

    elif st.session_state.active_tab == "Mitigation Hub" and user_role == "admin":
        st.header("🛡️ Automated Mitigation Hub")
        st.markdown("This AI-driven module executes predefined governance actions to neutralize threats in real-time.")
        
        if mitigations is not None and not mitigations.empty:
            miti_display = mitigations.copy()
            st.dataframe(
                miti_display[['timestamp', 'user_id', 'threat_type', 'action_taken', 'status']],
                column_config={
                    "timestamp": "Trigger Time",
                    "user_id": "Target User",
                    "threat_type": "Threat Vector",
                    "action_taken": "AI Action Applied",
                    "status": "Final Status"
                },
                hide_index=True,
                use_container_width=True
            )

            st.subheader("🕵️ Deep Forensic Explainability (XAI)")
            for _, row in mitigations.head(5).iterrows():
                with st.expander(f"Intelligence Report: {row['user_id']} ({row['timestamp']})"):
                    st.markdown(f"**Action Level:** `{row['action_taken']}`")
                    st.markdown(f"**Forensic Reasoning:**  \n{row['reasoning']}")
                    st.info(f"Status: {row['status']}")
            
            st.success(f"AI Engine has successfully neutralized {len(mitigations)} high-risk events.")
        else:
            st.info("Passive Mode: No mitigation actions have been triggered yet.")

    elif st.session_state.active_tab == "Threat Explanation":
        st.header("📊 Deep Threat Explanation")
        st.markdown("Detailed forensic analysis and explainable AI (XAI) for high-risk users.")
        
        high_risk_users = ml_features_df.sort_values(by='ml_risk_score', ascending=False)['user_id'].unique()[:10] if not ml_features_df.empty else []
        
        if len(high_risk_users) > 0:
            col_sel, col_empty = st.columns([1, 2])
            with col_sel:
                selected_user_xai = st.selectbox("Select Target for Analysis:", high_risk_users)
            
            st.divider()
            
            emp_info = get_employee_info(employees, selected_user_xai) or {'status': 'guest', 'role': 'External', 'department': 'Remote'}
            real_name = emp_info.get('employee_name', selected_user_xai)
            user_ml_stats = ml_features_df[ml_features_df['user_id'] == selected_user_xai].iloc[0].to_dict()
            
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.markdown(f"""
                <div class="explanation-card" style="text-align:center;">
                    <p style="color:#8b949e; margin-bottom:5px;">COMPOSITE RISK SCORE</p>
                    <div class="risk-gauge">{round(user_ml_stats['ml_risk_score'], 1)}%</div>
                    <p style="color:{'#ff7b72' if user_ml_stats['ml_risk_score'] > 70 else '#ffa657'}; font-size:0.9rem; font-weight:bold;">
                        {'CRITICAL THREAT' if user_ml_stats['ml_risk_score'] > 70 else 'ELEVATED RISK'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="explanation-card">
                    <h4 style="color:#58a6ff; font-size:1rem; margin-bottom:15px;">Behavioral Indicators</h4>
                    <div class="behavioral-flag {'critical' if user_ml_stats.get('total_attachments',0) > 5 else ''}">Attachments: {int(user_ml_stats.get('total_attachments',0))}</div>
                    <div class="behavioral-flag {'critical' if user_ml_stats.get('emails_after_hours',0) > 2 else ''}">After-Hours: {int(user_ml_stats.get('emails_after_hours',0))}</div>
                    <div class="behavioral-flag {'critical' if user_ml_stats.get('suspicious_keyword_count',0) > 0 else ''}">Keywords: {int(user_ml_stats.get('suspicious_keyword_count',0))}</div>
                    <div class="behavioral-flag">Logins: {int(user_ml_stats.get('logins',0))}</div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="explanation-card">
                    <h4 style="color:#58a6ff; font-size:1rem; margin-bottom:10px;">Forensic Profile: {real_name}</h4>
                    <p style="margin:2px 0; font-size:0.9rem;"><b>Role:</b> {emp_info.get('role', 'N/A')} | <b>Dept:</b> {emp_info.get('department', 'N/A')}</p>
                    <p style="margin:2px 0; font-size:0.9rem;"><b>Status:</b> <span style="color:{'#ff4b4b' if emp_info['status']=='ex' else '#3fb950'}">{emp_info['status'].upper()}</span></p>
                    <hr style="border-color:#30363d; margin:15px 0;">
                    <h5 style="color:#8b949e; font-size:0.9rem;">XAI Logic & Reasoning</h5>
                """, unsafe_allow_html=True)
                
                # Analyze using masked PII
                engine_xai = LLMEngine(use_mock=True)
                summary_xai = summarize_user_activity(emails, get_user_psychometrics(psychs, selected_user_xai), selected_user_xai, user_ml_stats, synthetic, emp_info)
                analysis_xai = engine_xai.analyze_user(summary_xai, user_id=selected_user_xai, real_name=real_name)
                
                st.write(analysis_xai.get('forensic_reasoning', 'Analysis pending...'))
                st.markdown("---")
                st.markdown(f"**Recommended Action:** `{analysis_xai.get('governance_action', 'Observe')}`")
                st.markdown("</div>", unsafe_allow_html=True)
                
            st.subheader("Physical Activity Trace (24h)")
            user_trace = synthetic[synthetic['user_id'] == selected_user_xai].sort_values(by='timestamp', ascending=False).head(20)
            if not user_trace.empty:
                st.dataframe(user_trace, use_container_width=True, hide_index=True)
            else:
                st.info("No system log activity found for this user in the trace window.")
        else:
            st.warning("No high-risk users identified in the current sample for explanation.")

    elif st.session_state.active_tab == "Live System Audit" and user_role == "admin":
        st.header("🌐 Local Host Governance Audit")
        monitor = SystemMonitor()
        st.dataframe(monitor.get_running_services().head(10), use_container_width=True)
        st.dataframe(monitor.get_network_connections().head(10), use_container_width=True)

    st.markdown("<br><hr><center style='color:#8b949e; font-size:0.7rem;'>ThreatSentinel v2.5.0-Enterprise | Hybrid AI SOC Framework</center>", unsafe_allow_html=True)
