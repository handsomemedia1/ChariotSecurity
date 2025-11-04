from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os
from shared.config.settings import settings

class EncryptionService:
    def __init__(self):
        # Derive key from settings
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'chariot_security_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(
            kdf.derive(settings.ENCRYPTION_KEY.encode())
        )
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        '''Encrypt string data'''
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        '''Decrypt encrypted data'''
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def encrypt_dict(self, data: dict) -> dict:
        '''Encrypt sensitive fields in dictionary'''
        import json
        json_str = json.dumps(data)
        return self.encrypt(json_str)
    
    def decrypt_dict(self, encrypted_data: str) -> dict:
        '''Decrypt dictionary'''
        import json
        decrypted_str = self.decrypt(encrypted_data)
        return json.loads(decrypted_str)

encryption_service = EncryptionService()
