
import sys
import os

# Add the current directory to path so we can import internal modules
sys.path.append(os.getcwd())

from insider_threat_system.data_loader import load_emails, load_psychometrics, get_user_psychometrics
from insider_threat_system.summarizer import summarize_user_activity
from insider_threat_system.ml_engine import MLRiskEngine

def main():
    print("Loading data...")
    # Adjust paths if necessary. Assuming running from project root
    email_path = 'archive(6)/email.csv'
    psychometric_path = 'archive(6)/psychometric.csv'
    
    try:
        emails = load_emails(email_path, sample_size=5000)
        print(f"Loaded {len(emails)} emails.")
        print("Email columns:", emails.columns.tolist())
        print("Sample email user:", emails['user'].iloc[0])
        
        psychometrics = load_psychometrics(psychometric_path)
        print(f"Loaded {len(psychometrics)} psychometric profiles.")
        print("Psychometric columns:", psychometrics.columns.tolist())
        
        print("\nTraining ML Anomaly Detection Engine...")
        ml_engine = MLRiskEngine()
        ml_scores_df = ml_engine.train_and_score(emails, psychometrics)
        print(f"Computed ML risks for {len(ml_scores_df)} users.")
        
        # Pick a user from emails to test summary
        test_user = emails['user'].iloc[0]
        print(f"Testing summary for user: {test_user}")
        
        user_psych = get_user_psychometrics(psychometrics, test_user)
        print("User Psychometrics:", user_psych)
        
        user_ml_stats = None
        if not ml_scores_df.empty:
            stats = ml_scores_df[ml_scores_df['user_id'] == test_user]
            if not stats.empty:
                user_ml_stats = stats.iloc[0].to_dict()
                print("User ML Stats:", {k:v for k,v in user_ml_stats.items() if k in ['is_anomaly', 'ml_risk_score']})
        
        summary = summarize_user_activity(emails, user_psych, test_user, user_ml_stats=user_ml_stats)
        from insider_threat_system.llm_engine import LLMEngine
        llm = LLMEngine()
        analysis = llm.analyze_user(summary)
        print("\n--- LLM Classification ---")
        print(f"Classification / Threat Type: {analysis.get('threat_type')}")
        print(f"Explanation / Reasoning: {analysis.get('reasoning')}")
        print(f"Risk Score: {analysis.get('risk_score')}")
        print(f"Governance Action: {analysis.get('governance_action')}")
        print("----------------")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
