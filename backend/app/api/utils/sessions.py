import hashlib
import secrets


def generate_session_secret() -> str:
    return secrets.token_urlsafe(32)


def hash_session_secret(secret: str) -> str:
    # Store session token hashes as hex strings so they can be stored in String columns.
    return hashlib.sha256(secret.encode()).hexdigest()