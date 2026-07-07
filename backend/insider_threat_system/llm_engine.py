import json
import os
import requests
from insider_threat_system.anonymizer import PIIAnonymizer

class LLMEngine:
    """
    Enterprise LLM Orchestration Engine. 
    Supports dynamic routing between local models (Ollama) and cloud APIs (OpenAI/Azure).
    Integrates active PII masking for absolute corporate data privacy.
    """
    def __init__(self, use_mock=None, api_key=None, model=None, api_base=None):
        # Allow environment configuration or parameters
        self.provider = os.getenv("LLM_PROVIDER", "").lower()
        if not self.provider:
            use_mock_env = os.getenv("USE_MOCK_LLM", "true").lower() == "true"
            self.provider = "mock" if use_mock_env else "openai"
        
        # Override config if parameters are explicitly passed
        if use_mock is True:
            self.provider = "mock"
        elif use_mock is False:
            self.provider = "openai" if self.provider == "mock" else self.provider

        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        self.model = model or os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo" if self.provider == "openai" else "llama3")
        self.api_base = api_base or os.getenv("LLM_API_BASE")
        self.anonymizer = PIIAnonymizer()

    def analyze_user(self, summary_text, user_id=None, real_name=None):
        """
        Analyzes a user summary text and returns structured security classification.
        Integrates dynamic PII anonymization to mask identity before sending to external APIs.
        """
        # 1. Anonymize PII if user details are present
        original_summary = summary_text
        if user_id and real_name:
            summary_text = self.anonymizer.anonymize(summary_text, user_id, real_name)
            
        prompt = self._construct_prompt(summary_text)
        
        # 2. Call the chosen corporate LLM backend
        if self.provider == "mock":
            result = self._mock_analyze(summary_text)
        else:
            result = self._real_analyze(prompt)

        # 3. Deanonymize PII to restore names for SOC Analyst dashboard
        if user_id and real_name and result:
            for key in ["reasoning", "forensic_reasoning", "forensic_justification", "governance_action"]:
                if key in result and isinstance(result[key], str):
                    result[key] = self.anonymizer.deanonymize(result[key], user_id, real_name)
            
            # Clean up user details inside extracted metadata
            if "extracted_metadata" in result:
                result["extracted_metadata"]["user_id"] = user_id
                result["extracted_metadata"]["employee_name"] = real_name

        return result

    def _construct_prompt(self, summary_text):
        return f"""
You are a cybersecurity insider threat detection expert focusing on Password-Based Threats and Access Governance.

{summary_text}

Analyze the data above and perform the following tasks:
1. Classify the threat type into EXACTLY one of: [Password Leakage, Governance Violation, No Threat].
2. Identify suspicious signals (e.g., sharing credentials, login outside normal hours, ex-employee login, role mismatch).
3. Assign a Risk Score (0-100) and Confidence Level (Low/Medium/High).
4. Provide a Governance Action recommendation.

Output Format (STRICT JSON):
{{
    "threat_type": "Password Leakage | Governance Violation | No Threat",
    "risk_score": 85,
    "confidence_level": "High",
    "suspicious_signals": ["sharing password via email", "after-hours login"],
    "reasoning": "Detailed justification here...",
    "governance_action": "Disable account and alert SOC",
    "extracted_metadata": {{
        "location": "...",
        "ip": "...",
        "device": "...",
        "employee_status": "current/ex"
    }}
}}
"""

    def _real_analyze(self, prompt):
        """Sends the payload to the active enterprise LLM provider."""
        try:
            if self.provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                }
                response = requests.post(url, headers=headers, json=payload, timeout=15)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
                
            elif self.provider == "ollama":
                # Connect to local Ollama server running inside enterprise VPC
                base_url = self.api_base or "http://localhost:11434"
                url = f"{base_url}/api/chat"
                payload = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "format": "json"
                }
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                content = data["message"]["content"]
                return json.loads(content)
                
            else:
                # Default back to mock if provider is invalid
                return self._mock_analyze(prompt)
        except Exception as e:
            # Fallback with error logging so security analysts always see data
            mock_res = self._mock_analyze(prompt)
            mock_res["reasoning"] = f"⚠️ [LLM API Fallback: {e}] " + mock_res["reasoning"]
            return mock_res

    def _mock_analyze(self, text):
        text_lower = text.lower()
        
        # Meta-extraction
        def extract(key, text):
            for line in text.split('\n'):
                if f"- {key}:" in line:
                    return line.split(':', 1)[1].strip()
            return "N/A"

        status = extract("Status", text)
        ip = extract("Sender IP", text)
        if ip == "N/A": 
            ip = extract("IP", text)

        loc = extract("Recent Message Origin", text)
        if loc == "N/A":
            loc = extract("Location", text)

        dev = extract("Device", text)
        
        signals = []
        risk = 10
        threat = "No Threat"
        action = "Log only"
        
        # Threat Type 1: Password Leakage
        trigger_words = ["admin", "password", "root", "vpn keys", "credentials", "secret", "token"]
        if any(w in text_lower for w in trigger_words):
            threat = "Password Leakage"
            risk = 90
            signals.append("Sensitive credential sharing detected")
            action = "Immediately disable account and reset passwords."
        
        # Location Anomaly Check
        if loc != "N/A" and loc != "Internal Corporate HQ" and "Unknown" not in loc:
            risk = min(100, risk + 15)
            signals.append(f"Location Anomaly: Activity originating from {loc}")
            if threat == "No Threat":
                threat = "Governance Violation"
                action = "Review access logs for foreign IP."

        # Threat Type 2: Governance Violation (Ex-Employee)
        if status.lower() == "ex" and ("login" in text_lower or threat != "No Threat"):
            threat = "Governance Violation"
            risk = 100
            signals.append("Ex-employee account active")
            action = "Critical: Auto-deactivate user account."
            
        # MITRE ATT&CK Mapping
        mitre_db = {
            "Password Leakage": {"id": "T1552", "name": "Unsecured Credentials"},
            "Governance Violation": {"id": "T1078", "name": "Valid Accounts - Misuse"},
            "No Threat": {"id": "N/A", "name": "Standard Activity"}
        }

        mapping = mitre_db.get(threat, mitre_db["No Threat"])
        
        return {
            "threat_type": threat,
            "risk_score": risk,
            "confidence_level": "High" if len(signals) > 1 else "Medium",
            "suspicious_signals": signals,
            "reasoning": f"Detection: {threat} identified based on signals: {', '.join(signals)}.",
            "forensic_reasoning": f"Deep Forensic Analysis: User status '{status}' cross-referenced with {len(signals)} markers. MITRE Technique {mapping['id']} ({mapping['name']}) identified.",
            "mitre_mapping": mapping,
            "forensic_justification": f"System confirmed possible {threat} intent. MITRE Technique {mapping['id']} applied.",
            "governance_action": action,
            "extracted_metadata": {"location": loc, "ip": ip, "device": dev, "employee_status": status}
        }
