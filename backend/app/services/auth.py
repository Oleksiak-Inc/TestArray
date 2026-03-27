from sqlalchemy.orm import Session
from db.models.users import Users
from db.models.sessions import Sessions as UserSessions
from app.api.utils.auth import hash_password, verify_password
from datetime import datetime, timedelta, timezone

from core.config import settings
from app.services.users import UserService
from app.services.session import SessionService
from app.services.user_type import UserTypeService
from utils.service import BaseService


class AuthService(BaseService):

    def login_user(self, email: str, password: str):
        user = UserService(self.db).get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None

        now = datetime.now(timezone.utc)
        exp = now + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)

        session_secret = SessionService(self.db).create_session(user.id, exp, now)

        user.last_login_at = now
        self.commit_and_refresh(user)

        return {"user": user, "access_token": session_secret}
    
    def validate_session(self, session_secret: str):
        session = SessionService(self.db).get_session(session_secret=session_secret)
        if not session:
            return False
        
        if session.expires_at < datetime.now(timezone.utc):
            SessionService(self.db).delete_session(session_secret)
            return False
        
        user = UserService(self.db).get_user_by_id(session.user_id)
        if not user or not user.active:
            return False
        
        return True
    
    def register_user(self, first_name: str, last_name: str, email: str, password: str):
        existing_user = self.db.query(Users).filter(Users.email == email).first()
        regular_user_type = UserTypeService(self.db).get_user_type_by_name("regular")
        
        if existing_user:
            return None
        
        if not regular_user_type:
            return None
        
        hashed_password = hash_password(password)
        new_user = Users(
            first_name=first_name, 
            last_name=last_name, 
            email=email, 
            password=hashed_password, 
            user_type_id=regular_user_type.id
            )
        self.db.add(new_user)
        self.commit_and_refresh(new_user)
        return new_user

    def logout_user(self, session_secret: str):
        session = SessionService(self.db).delete_session(session_secret)
        
        if not session:
            return None
        
        return True

    