
from db.models.users import Users
from datetime import datetime, timedelta, timezone

from core.config import settings
from app.services.users import UserService
from app.services.session import SessionService
from .utils.service import BaseService
from core.security import PasswordHasher


class AuthService(BaseService):

    def login_user(self, email: str, password: str, request=None):
        user = UserService(self.db).get_user_by_email(email)
        if not user:
            return None
        if not user.password or not PasswordHasher.verify(password, user.password):
            return None

        now = datetime.now(timezone.utc)
        exp = now + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)

        user_agent = request.headers.get("user-agent") if request is not None else None
        ip_address = request.client.host if request is not None and request.client is not None else None

        session_secret = SessionService(self.db).create_session(
            user.id,
            exp,
            now,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        self.update(user, {"last_login_at": now})

        return {"user": user, "access_token": session_secret, "expires_at": exp.timestamp()}

    def validate_session(self, session_secret: str):
        session = SessionService(self.db).get_session(session_secret=session_secret)
        if not session:
            return False

        ended_at = session.ended_at
        if ended_at.tzinfo is None:
            ended_at = ended_at.replace(tzinfo=timezone.utc)
        if ended_at <= datetime.now(timezone.utc):
            return False

        user = UserService(self.db).get_user_by_id(session.user_id)
        if not user or not user.active or not user.password:
            return False

        return True
    
    def register_user(self, first_name: str, last_name: str, email: str, password: str):
        existing_user = self.db.query(Users).filter(Users.email == email).first()
        if existing_user:
            return None

        hashed_password = PasswordHasher.hash(password)
        return self.create(
            Users,
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": hashed_password,
            },
        )

    def logout_user(self, session_secret: str):
        session = SessionService(self.db).delete_session(session_secret)

        if not session:
            return None

        return True

    