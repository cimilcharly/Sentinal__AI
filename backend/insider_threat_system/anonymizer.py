import re

class PIIAnonymizer:
    """
    Anonymization engine to mask Personally Identifiable Information (PII) 
    such as names and emails from behavior summaries before sending to external LLMs.
    """
    def __init__(self):
        pass

    def anonymize(self, text, user_id, real_name=None):
        """
        Masks all occurrences of real names and email addresses in the text
        with anonymous tokens.
        """
        if not text:
            return text
            
        masked_text = text
        
        # 1. Mask the specific real name if provided
        if real_name:
            # Case-insensitive name replacement
            pattern = re.compile(re.escape(real_name), re.IGNORECASE)
            masked_text = pattern.sub(f"Employee {user_id}", masked_text)
            
            # Mask just the last name if it's multiple words
            name_parts = real_name.split()
            if len(name_parts) > 1:
                last_name = name_parts[-1]
                if len(last_name) > 2:  # Avoid single character mistakes
                    ln_pattern = re.compile(re.escape(last_name), re.IGNORECASE)
                    masked_text = ln_pattern.sub(f"Employee {user_id}", masked_text)

        # 2. Mask all corporate or external email addresses
        # Matches typical email formats
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        masked_text = re.sub(email_pattern, f"user_{user_id.lower()}@company.com", masked_text)
        
        # 3. Mask any external looking IP addresses for standard network protection
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        masked_text = re.sub(ip_pattern, "10.0.0.XXX", masked_text)

        return masked_text

    def deanonymize(self, text, user_id, real_name):
        """
        Restores real names and typical company details back into the LLM output 
        before displaying to the SOC analyst.
        """
        if not text or not real_name:
            return text
            
        restored_text = text
        # Restore Employee ID token to Real Name
        token = f"Employee {user_id}"
        restored_text = re.sub(re.escape(token), real_name, restored_text, flags=re.IGNORECASE)
        
        # Restore Email token to standard format
        email_token = f"user_{user_id.lower()}@company.com"
        real_email = f"{user_id.lower()}@company.com"
        restored_text = re.sub(re.escape(email_token), real_email, restored_text, flags=re.IGNORECASE)
        
        return restored_text
