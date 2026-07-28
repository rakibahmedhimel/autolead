import base64
import hashlib
from cryptography.fernet import Fernet
from backend.app.config import API_KEY_ENCRYPTION_SECRET


def _fernet() -> Fernet:
    if not API_KEY_ENCRYPTION_SECRET:
        raise RuntimeError("API_KEY_ENCRYPTION_SECRET is not configured")
    key = base64.urlsafe_b64encode(hashlib.sha256(API_KEY_ENCRYPTION_SECRET.encode()).digest())
    return Fernet(key)


def encrypt_key(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt_key(value: str) -> str:
    return _fernet().decrypt(value.encode()).decode()


def masked_key(suffix: str) -> str:
    return f"fc-****{suffix}"
