import sqlite3
import pandas as pd

conn = sqlite3.connect('forensics_audit.db')
query = "SELECT id, date, user_id, content FROM emails ORDER BY date DESC LIMIT 10"
df = pd.read_sql(query, conn)
print("Latest 10 emails in DB (Sorted by Date DESC):")
print(df[['id', 'date', 'user_id']])
if not df.empty:
    print("\nFull record 0:")
    print(df.iloc[0])

# Check for specific today date
today = "2026-03-12"
query_today = f"SELECT count(*) FROM emails WHERE date LIKE '{today}%'"
count_today = conn.execute(query_today).fetchone()[0]
print(f"\nEmails found for {today}: {count_today}")

conn.close()
