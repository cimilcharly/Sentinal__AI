"""Security utilities for data protection and encryption."""

import os
import hashlib
import hmac
from cryptography.fernet import Fernet
from typing import Dict, Any


class EncryptionManager:
    """Manages encryption/decryption of sensitive data."""

    def __init__(self):
        # In production, load from secure key management service (AWS KMS, HashiCorp Vault)
        key = os.getenv("ENCRYPTION_KEY", "dev-key-change-in-production")
        self.cipher = Fernet(self._derive_key(key))

    @staticmethod
    def _derive_key(key: str) -> bytes:
        """Derive encryption key from string."""
        return Fernet.generate_key() if key == "dev-key-change-in-production" else key.encode()

    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in dictionary."""
        sensitive_fields = ["password", "token", "secret", "api_key", "credentials"]
        encrypted = data.copy()

        for field in sensitive_fields:
            if field in encrypted and encrypted[field]:
                encrypted[field] = self.encrypt(str(encrypted[field]))

        return encrypted

    def decrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in dictionary."""
        sensitive_fields = ["password", "token", "secret", "api_key", "credentials"]
        decrypted = data.copy()

        for field in sensitive_fields:
            if field in decrypted and decrypted[field]:
                try:
                    decrypted[field] = self.decrypt(decrypted[field])
                except:
                    pass  # Field not encrypted

        return decrypted


class DataMasking:
    """Mask sensitive data for logs and displays."""

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address."""
        if "@" not in email:
            return email
        local, domain = email.split("@")
        return f"{local[0]}***@{domain}"

    @staticmethod
    def mask_ip(ip: str) -> str:
        """Mask IP address."""
        parts = ip.split(".")
        return f"{parts[0]}.{parts[1]}.***.*"

    @staticmethod
    def mask_token(token: str, visible_chars: int = 4) -> str:
        """Mask API token."""
        if len(token) <= visible_chars:
            return "***"
        return f"{token[:visible_chars]}{'*' * (len(token) - visible_chars)}"

    @staticmethod
    def mask_pii(data: Dict[str, Any]) -> Dict[str, Any]:
        """Mask PII fields in dictionary."""
        masked = data.copy()
        pii_fields = {
            "email": DataMasking.mask_email,
            "ip_address": DataMasking.mask_ip,
            "api_key": DataMasking.mask_token,
            "phone": lambda x: f"***-***-{x[-4:]}",
        }

        for field, mask_func in pii_fields.items():
            if field in masked and masked[field]:
                try:
                    masked[field] = mask_func(str(masked[field]))
                except:
                    pass

        return masked


class PasswordSecurity:
    """Password hashing and validation."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt-like approach."""
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hash_: str) -> bool:
        """Verify password against hash."""
        import bcrypt
        try:
            return bcrypt.checkpw(password.encode(), hash_.encode())
        except:
            return False

    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key."""
        import secrets
        return f"sk_{secrets.token_hex(32)}"


class AuditTrail:
    """Comprehensive audit logging for compliance."""

    @staticmethod
    def log_data_access(
        tenant_id: str,
        user_id: str,
        resource: str,
        action: str,
        result: str = "success"
    ):
        """Log data access for GDPR/HIPAA compliance."""
        log_entry = {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "result": result,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
        # In production, send to dedicated audit log system
        return log_entry

    @staticmethod
    def log_data_export(tenant_id: str, user_id: str, scope: str):
        """Log data export for GDPR compliance."""
        return AuditTrail.log_data_access(
            tenant_id, user_id, "entire_tenant", "data_export"
        )

    @staticmethod
    def log_data_deletion(tenant_id: str, user_id: str, scope: str):
        """Log data deletion for GDPR/retention policies."""
        return AuditTrail.log_data_access(
            tenant_id, user_id, scope, "data_deletion"
        )
