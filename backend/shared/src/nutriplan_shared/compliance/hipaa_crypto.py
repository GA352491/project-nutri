from cryptography.fernet import Fernet
import os

class HIPAAEncryptionService:
    """
    Handles encryption/decryption of Personally Identifiable Information (PII) 
    and Protected Health Information (PHI) at rest, as required by HIPAA.
    """
    def __init__(self):
        # In production, this key must be injected via a secure secrets manager (e.g. AWS KMS or Hashicorp Vault)
        # For MVP/local testing, we'll generate an ephemeral one if not found in env
        key_str = os.environ.get("HIPAA_ENCRYPTION_KEY")
        if not key_str:
            self._key = Fernet.generate_key()
            print("[WARN] Using ephemeral HIPAA encryption key. Data will be unrecoverable on restart.")
        else:
            self._key = key_str.encode('utf-8')
            
        self.fernet = Fernet(self._key)

    def encrypt_phi(self, plain_text: str) -> str:
        """Encrypts sensitive health data before storing in DB."""
        if not plain_text:
            return plain_text
        return self.fernet.encrypt(plain_text.encode('utf-8')).decode('utf-8')

    def decrypt_phi(self, cipher_text: str) -> str:
        """Decrypts sensitive health data upon retrieval from DB."""
        if not cipher_text:
            return cipher_text
        return self.fernet.decrypt(cipher_text.encode('utf-8')).decode('utf-8')

hipaa_crypto = HIPAAEncryptionService()
