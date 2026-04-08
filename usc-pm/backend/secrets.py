"""Encrypt OAuth tokens at rest using Fernet."""
import os
import json
import base64
import hashlib
from cryptography.fernet import Fernet


def _key() -> bytes:
    raw = os.environ.get("ENCRYPTION_KEY")
    if not raw:
        raise RuntimeError("ENCRYPTION_KEY not set")
    # Accept hex or raw; derive a 32-byte Fernet key
    digest = hashlib.sha256(raw.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_json(obj: dict) -> bytes:
    return Fernet(_key()).encrypt(json.dumps(obj).encode())


def decrypt_json(blob: bytes) -> dict:
    return json.loads(Fernet(_key()).decrypt(blob).decode())
