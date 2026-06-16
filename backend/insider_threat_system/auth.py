import os
import yaml
import streamlit_authenticator as stauth

CONFIG_PATH = os.path.join("config", "auth_config.yaml")

def init_auth_config():
    """Initializes the secure YAML configuration file for user authentication if it does not exist."""
    os.makedirs("config", exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        print("[KEY] Initializing default security credentials (auth_config.yaml)...")
        
        # Generate bcrypt hashes for default administrative and analyst accounts
        passwords_to_hash = ['admin123', 'analyst123']
        try:
            # stauth Hasher handles secure salting and hashing
            hasher = stauth.Hasher(passwords_to_hash)
            hashed_passwords = hasher.generate()
        except Exception:
            # Fallback if stauth has a different API signature in installed version
            import bcrypt
            hashed_passwords = [
                bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') 
                for p in passwords_to_hash
            ]
            
        config = {
            "credentials": {
                "usernames": {
                    "admin": {
                        "email": "admin-soc@company.com",
                        "name": "System Administrator",
                        "password": hashed_passwords[0],
                        "role": "admin"
                    },
                    "analyst": {
                        "email": "analyst-soc@company.com",
                        "name": "Security Analyst",
                        "password": hashed_passwords[1],
                        "role": "analyst"
                    }
                }
            },
            "cookie": {
                "expiry_days": 30,
                "key": "threat_sentinel_cookie_key",
                "name": "threat_sentinel_cookie"
            },
            "pre-authorized": {
                "emails": [
                    "admin-soc@company.com",
                    "analyst-soc@company.com"
                ]
            }
        }
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        print("[OK] Credentials initialized successfully.")
        print("  - Admin: admin / admin123")
        print("  - Analyst: analyst / analyst123")

def load_auth_config():
    """Loads and returns the YAML security config."""
    init_auth_config()
    with open(CONFIG_PATH, "r") as f:
        return yaml.load(f, Loader=SafeLoaderHelper)

# Helper YAML Loader class to prevent injection vulnerabilities
class SafeLoaderHelper(yaml.SafeLoader):
    pass
