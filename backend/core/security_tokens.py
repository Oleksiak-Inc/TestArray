import hashlib
import secrets

class SessionTokenFactory:
    @staticmethod
    def generate_secret() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_secret(secret: str) -> str:
        return hashlib.sha256(secret.encode()).hexdigest()