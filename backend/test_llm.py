
import sys
import os

sys.path.append(os.getcwd())

from insider_threat_system.llm_engine import LLMEngine

def test_llm():
    print("Testing LLM Engine (Mock Mode)...")
    engine = LLMEngine(use_mock=True)
    
    # Test Case 1: Suspicious
    summary_suspicious = "User sent emails with subject 'Project X Secret' and content containing 'keylogger' and 'upload'."
    print(f"\nInput: {summary_suspicious}")
    result = engine.analyze_user(summary_suspicious)
    print("Result:", result)
    assert result['classification'] == 'Malicious'
    
    # Test Case 2: Negligent
    summary_negligent = "User downloaded proprietary manuals to personal device."
    print(f"\nInput: {summary_negligent}")
    result = engine.analyze_user(summary_negligent)
    print("Result:", result)
    assert result['classification'] == 'Negligent'
    
    # Test Case 3: Normal
    summary_normal = "User sent 5 items regarding meeting schedule."
    print(f"\nInput: {summary_normal}")
    result = engine.analyze_user(summary_normal)
    print("Result:", result)
    assert result['classification'] == 'Normal'
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_llm()
