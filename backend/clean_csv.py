
import pandas as pd
import os

path = 'archive(6)/email.csv'
if os.path.exists(path):
    print(f"Reading {path}...")
    try:
        # Try reading but ignore bad lines
        df = pd.read_csv(path, on_bad_lines='skip')
        print(f"Loaded {len(df)} lines after skipping bad ones.")
        
        # Save a clean copy
        df.to_csv(path, index=False, quoting=1)
        print("Cleaned file saved.")
        
        # Verify LIVE emails
        live = df[df['id'].astype(str).str.startswith('LIVE_')]
        print(f"Verified {len(live)} LIVE emails in the clean file.")
        if not live.empty:
            print("Last LIVE email found:")
            print(live.tail(1))
    except Exception as e:
        print(f"Error: {e}")
