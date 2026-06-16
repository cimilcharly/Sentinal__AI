import os
import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///forensics_audit.db")

print(f"🛠️ Connecting to Forensic Database via SQLAlchemy: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

# SQLAlchemy setup
engine = create_engine(
    DATABASE_URL,
    pool_size=10 if "sqlite" not in DATABASE_URL else 5,
    max_overflow=20 if "sqlite" not in DATABASE_URL else 0,
    pool_recycle=3600
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- ORM Models ---

class Employee(Base):
    __tablename__ = 'employees'
    employee_id = Column(Integer)
    user_id = Column(String(50), primary_key=True)
    name = Column(String(100))
    status = Column(String(20))
    role = Column(String(100))
    department = Column(String(100))
    last_working_day = Column(String(50))
    email = Column(String(255))

class Email(Base):
    __tablename__ = 'emails'
    id = Column(String(100), primary_key=True)
    date = Column(DateTime)
    user_id = Column(String(50))
    pc = Column(String(50))
    recipient = Column(Text)
    sender = Column(String(255))
    attachments = Column(Integer, default=0)
    content = Column(Text)
    origin_ip = Column(String(50))
    location = Column(String(100))
    destination_ip = Column(String(50))

class SystemLog(Base):
    __tablename__ = 'system_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)
    user_id = Column(String(50))
    pc = Column(String(50))
    activity_type = Column(String(50))
    resource = Column(Text)
    details = Column(Text)
    ip = Column(String(50))
    location = Column(String(100))
    device = Column(String(50))
    is_anomaly = Column(Integer, default=0)

class Psychometric(Base):
    __tablename__ = 'psychometrics'
    employee_name = Column(String(100))
    user_id = Column(String(50), primary_key=True)
    O = Column(Float)
    C = Column(Float)
    E = Column(Float)
    A = Column(Float)
    N = Column(Float)

class MitigationLog(Base):
    __tablename__ = 'mitigation_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String(50))
    user_id = Column(String(50))
    threat_type = Column(String(100))
    action_taken = Column(String(100))
    reasoning = Column(Text)
    status = Column(String(50))

def init_db():
    print("🧹 Creating enterprise database schema...")
    Base.metadata.create_all(engine)
    print("✅ Database schema created successfully.")

def migrate_csv_to_sql():
    # Paths to existing CSVs
    csv_mappings = {
        'archive(6)/employee_database.csv': 'employees',
        'archive(6)/email.csv': 'emails',
        'archive(6)/synthetic_activity.csv': 'system_logs',
        'archive(6)/psychometric.csv': 'psychometrics'
    }

    for csv_path, table_name in csv_mappings.items():
        if os.path.exists(csv_path):
            print(f"📦 Migrating {csv_path} -> {table_name}...")
            try:
                df = pd.read_csv(csv_path)
                
                # Cleanup if necessary (mapping column names)
                if table_name == 'emails':
                    # CSV order: id,date,user,pc,to,from,attachments,content
                    df.columns = ['id', 'date', 'user_id', 'pc', 'recipient', 'sender', 'attachments', 'content']
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    # Keep database keys clean of duplicates
                    df = df.drop_duplicates(subset=['id'])
                    for col in ['origin_ip', 'location', 'destination_ip']:
                        if col not in df.columns:
                            df[col] = "Internal Network" if col == 'location' else "127.0.0.1"
                
                if table_name == 'employees':
                    # Add dummy emails for demo mapping if not present
                    if 'email' not in df.columns:
                        df['email'] = df['user_id'].apply(lambda x: "testese2026@gmail.com" if x == 'USR001' else f"{x.lower()}@company.com")
                
                if table_name == 'system_logs':
                    # CSV order: user_id,timestamp,action,resource,details,ip,location,device,is_anomaly
                    df.columns = ['user_id', 'timestamp', 'activity_type', 'resource', 'details', 'ip', 'location', 'pc', 'is_anomaly']
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                    df['device'] = df['pc'] # duplicate device column for system_logs database schema

                # Truncate tables for fresh seed using ORM engine
                with engine.connect() as conn:
                    # Execute drop/recreate on tables being seeded to prevent duplicate key errors
                    if table_name == 'employees':
                        Employee.__table__.drop(engine, checkfirst=True)
                        Employee.__table__.create(engine)
                    elif table_name == 'emails':
                        Email.__table__.drop(engine, checkfirst=True)
                        Email.__table__.create(engine)
                    elif table_name == 'system_logs':
                        SystemLog.__table__.drop(engine, checkfirst=True)
                        SystemLog.__table__.create(engine)
                    elif table_name == 'psychometrics':
                        Psychometric.__table__.drop(engine, checkfirst=True)
                        Psychometric.__table__.create(engine)

                # Use append to preserve SQLAlchemy constraints
                df.to_sql(table_name, engine, if_exists='append', index=False)
                print(f"  - Successfully imported {len(df)} records.")
            except Exception as e:
                print(f"  - ❌ Error migrating {csv_path}: {e}")
        else:
            print(f"  - ⚠️ Skipping {csv_path}: File not found.")

    print("\n🚀 Migration complete! The system is now hardware-ready for high-volume forensics.")

if __name__ == "__main__":
    init_db()
    migrate_csv_to_sql()
