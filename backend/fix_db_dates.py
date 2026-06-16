import sqlite3
import pandas as pd
from email.utils import parsedate_to_datetime
import datetime

conn = sqlite3.connect('forensics_audit.db')
cursor = conn.cursor()

print("Converting email dates to ISO format...")
emails = cursor.execute("SELECT id, date FROM emails").fetchall()

updates = []
for msg_id, date_str in emails:
    try:
        # Check if already ISO (YYYY-MM-DD ...)
        datetime.datetime.strptime(date_str[:10], '%Y-%m-%d')
        continue # Already ISO
    except ValueError:
        pass
        
    try:
        dt = parsedate_to_datetime(date_str)
        iso_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        updates.append((iso_date, msg_id))
    except Exception as e:
        print(f"Failed to parse {date_str} for ID {msg_id}: {e}")

if updates:
    print(f"Updating {len(updates)} records...")
    cursor.executemany("UPDATE emails SET date = ? WHERE id = ?", updates)
    conn.commit()
    print("Optimization complete.")
else:
    print("No records needed updating.")

conn.close()
