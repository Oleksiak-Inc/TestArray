
from datetime import datetime
from db.models.sessions import Sessions
from core.security_tokens import SessionTokenFactory
from .utils.service import BaseService

class SessionService(BaseService):

    def create_session(self, user_id: int, expires_at: datetime, created_at: datetime) -> str:
        
        session_secret = SessionTokenFactory.generate_secret()
        session_hash = SessionTokenFactory.hash_secret(session_secret)

        session = Sessions(
            user_id=user_id,
            token=session_hash,
            created_at=created_at,
            expires_at=expires_at
        )
        self.save(session, refresh=True)
        return session_secret
    
    def get_session(self, session_secret: str):
        session_hash = SessionTokenFactory.hash_secret(session_secret)
        session = self.db.query(Sessions).filter(Sessions.token == session_hash).first()
        if not session:
            return None
        return session
    
    def delete_session(self, session_secret: str):
        session = self.get_session(session_secret)
        
        if not session:
            return None
        
        return self.delete(session)
    
    def delete_all_sessions(self, user_id: int):
        sessions = self.db.query(Sessions).filter(Sessions.user_id == user_id).all()
        
        for session in sessions:
            self.db.delete(session)
        self.commit()
        return sessions