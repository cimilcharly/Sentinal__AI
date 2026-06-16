import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "forensics_audit.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Setup SQLAlchemy connection engine for the data loader
engine = create_engine(
    DATABASE_URL,
    pool_size=10 if "sqlite" not in DATABASE_URL else 5,
    max_overflow=20 if "sqlite" not in DATABASE_URL else 0,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_connection():
    """Helper to return an active SQLAlchemy database connection."""
    try:
        return engine.connect()
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def load_psychometrics(path=None):
    """Loads psychometric data from SQLite/Postgres (psychometrics table)."""
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        df = pd.read_sql("SELECT * FROM psychometrics", conn)
    finally:
        conn.close()
    return df

def load_emails(path=None, sample_size=50000):
    """Loads emails from SQLite/Postgres (emails table). Newest first."""
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    
    # Map back to our expected internal columns: id, date, user, pc, to, from, attachments, content
    query = f"""
        SELECT id, date, user_id as user, pc, recipient as 'to', sender as 'from', attachments, content,
               origin_ip, location, destination_ip
        FROM emails 
        ORDER BY date DESC 
        LIMIT {sample_size}
    """
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    
    # Ensure date is datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

def get_user_psychometrics(psychometric_df, user_id):
    """Returns the psychometric scores for a specific user."""
    if psychometric_df is None or psychometric_df.empty or user_id not in psychometric_df['user_id'].values:
        return None
    user_row = psychometric_df[psychometric_df['user_id'] == user_id]
    return user_row.iloc[0].to_dict()

def load_synthetic_activity(path=None):
    """Loads system logs from SQLite/Postgres (system_logs table)."""
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    
    query = "SELECT timestamp, user_id, pc, activity_type as activity, details, is_anomaly FROM system_logs ORDER BY timestamp DESC"
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    return df

def load_mitigation_logs():
    """Loads the automated mitigation actions from SQLite/Postgres."""
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        df = pd.read_sql("SELECT * FROM mitigation_logs ORDER BY timestamp DESC", conn)
    except Exception:
        df = pd.DataFrame(columns=['id', 'timestamp', 'user_id', 'threat_type', 'action_taken', 'reasoning', 'status'])
    finally:
        conn.close()
    
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    return df

def load_employees_db(path=None):
    """Loads the employee database from SQLite/Postgres (employees table)."""
    conn = get_db_connection()
    if conn is None: return pd.DataFrame()
    try:
        df = pd.read_sql("SELECT * FROM employees", conn)
    finally:
        conn.close()
    return df

def get_employee_info(employee_df, user_id):
    """Retrieves full profile for a user from the employee database."""
    if employee_df is None or employee_df.empty or user_id not in employee_df['user_id'].values:
        return None
    row = employee_df[employee_df['user_id'] == user_id]
    return row.iloc[0].to_dict()
