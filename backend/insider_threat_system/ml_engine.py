import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class MLRiskEngine:
    def __init__(self):
        # We assume ~5% of users might be acting suspiciously in anomalies
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.scaler = StandardScaler()
        self.fitted = False

    def extract_features(self, emails_df, psychometric_df, synthetic_df=None):
        """
        Extract numeric features from raw log data to train the Machine Learning model.
        """
        user_stats = []
        if emails_df is not None and not emails_df.empty:
            for user, user_emails in emails_df.groupby('user'):
                total_emails = len(user_emails)
                
                # After hours activity (outside 6 AM - 7 PM)
                if 'date' in user_emails.columns:
                    # Explicitly convert to datetime to prevent .dt accessor crashes
                    user_dates = pd.to_datetime(user_emails['date'], errors='coerce')
                    after_hours = user_dates.dt.hour.apply(lambda h: 1 if pd.notna(h) and (h < 6 or h > 19) else 0).sum()
                else:
                    after_hours = 0
                    
                # Suspicious keywords presence
                suspicious_keywords = ['confidential', 'secret', 'proprietary', 'keylogger', 'download', 'upload']
                suspicious_count = user_emails['content'].fillna('').str.lower().apply(
                    lambda x: sum(1 for w in suspicious_keywords if w in x)
                ).sum()
                
                # Attachment tracking
                attachments = pd.to_numeric(user_emails['attachments'], errors='coerce').sum()
                
                user_stats.append({
                    'user_id': user,
                    'total_emails': total_emails,
                    'emails_after_hours': after_hours,
                    'suspicious_keyword_count': suspicious_count,
                    'total_attachments': attachments
                })
            
        features_df = pd.DataFrame(user_stats)
        
        # Merge advanced behavioral features from Synthetic Logs
        if synthetic_df is not None and not synthetic_df.empty:
            synth_features = []
            for user, user_logs in synthetic_df.groupby('user_id'):
                logins = len(user_logs[user_logs['activity'] == 'login'])
                usb_inserts = len(user_logs[user_logs['activity'] == 'usb_insert'])
                file_downloads = len(user_logs[user_logs['activity'] == 'file_download'])
                process_execs = len(user_logs[user_logs['activity'] == 'process_exec'])
                
                synth_features.append({
                    'user_id': user,
                    'logins': logins,
                    'usb_inserts': usb_inserts,
                    'file_downloads': file_downloads,
                    'process_execs': process_execs,
                    'emails_sent_synth': len(user_logs[user_logs['activity'] == 'email_send'])
                })
            
            synth_df = pd.DataFrame(synth_features)
            
            if not features_df.empty:
                features_df = features_df.merge(synth_df, on='user_id', how='outer')
            else:
                features_df = synth_df
            
            features_df.fillna(0, inplace=True)
        
        # Merge with user psychometric profiles
        if not features_df.empty and psychometric_df is not None and not psychometric_df.empty:
            features_df = features_df.merge(psychometric_df[['user_id', 'O', 'C', 'E', 'A', 'N']], on='user_id', how='left')
            # Fill missing psychometrics with population average
            for col in ['O', 'C', 'E', 'A', 'N']:
                if col in features_df.columns:
                     features_df[col] = features_df[col].fillna(features_df[col].median() if not features_df[col].isna().all() else 50)
            features_df.fillna(0, inplace=True) 
            
        return features_df

    def train_and_score(self, emails_df, psychometric_df, synthetic_df=None):
        """
        Trains the Isolation Forest algorithm on the extracted features to find anomalous users.
        """
        features_df = self.extract_features(emails_df, psychometric_df, synthetic_df)
        
        if features_df.empty:
            return pd.DataFrame()
            
        numeric_cols = ['total_emails', 'emails_after_hours', 'suspicious_keyword_count', 'total_attachments', 
                        'O', 'C', 'E', 'A', 'N',
                        'logins', 'usb_inserts', 'file_downloads', 'process_execs', 'emails_sent_synth']
        
        # Only use columns that exist
        numeric_cols = [col for col in numeric_cols if col in features_df.columns]
        
        if not numeric_cols:
            return pd.DataFrame()

        X = features_df[numeric_cols]
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Predict anomalies
        self.model.fit(X_scaled)
        features_df['is_anomaly'] = self.model.predict(X_scaled) == -1
        
        # Get raw risk scores.
        features_df['raw_risk'] = -self.model.decision_function(X_scaled)
        
        # Normalize ML risk score 0 to 100
        min_score = features_df['raw_risk'].min()
        max_score = features_df['raw_risk'].max()
        if max_score > min_score:
            features_df['ml_risk_score'] = ((features_df['raw_risk'] - min_score) / (max_score - min_score)) * 100
        else:
            features_df['ml_risk_score'] = 0
            
        self.fitted = True
        return features_df
