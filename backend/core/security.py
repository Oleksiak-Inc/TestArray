from passlib.context import CryptContext


class PasswordHasher:
    _pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    @classmethod
    def hash(cls, password: str) -> str:
        return cls._pwd_context.hash(password)

    @classmethod
    def verify(cls, plain_password: str, hashed_password: str) -> bool:
        return cls._pwd_context.verify(plain_password, hashed_password)