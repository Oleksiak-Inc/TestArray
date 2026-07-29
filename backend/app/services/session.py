
from datetime import datetime, timezone

from db.models.revocations import Revocations
from db.models.sessions import Sessions
from core.security_tokens import SessionTokenFactory
from .utils.service import BaseService


class SessionService(BaseService):

    def create_session(self, user_id: int, expires_at: datetime, created_at: datetime, user_agent: str | None = None, ip_address: str | None = None) -> str:
        session_secret = SessionTokenFactory.generate_secret()
        session_hash = SessionTokenFactory.hash_secret(session_secret)

        session = Sessions(
            user_id=user_id,
            token=session_hash,
            created_at=created_at,
            expires_at=expires_at,
            ended_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.save(session, refresh=True)
        return session_secret

    def get_session(self, session_secret: str):
        session_hash = SessionTokenFactory.hash_secret(session_secret)
        session = self.db.query(Sessions).filter(Sessions.token == session_hash).first()
        if not session:
            return None
        return session

    def get_active_sessions_for_user(self, user_id: int):
        now = datetime.now(timezone.utc)
        return self.db.query(Sessions).filter(Sessions.user_id == user_id, Sessions.ended_at > now).all()

    def revoke_session(self, session_secret: str, revoked_by_user_id: int | None = None, incident_id: int | None = None):
        session = self.get_session(session_secret)
        if not session:
            return None

        if revoked_by_user_id is None:
            revoked_by_user_id = session.user_id

        return self.revoke_session_by_instance(session, revoked_by_user_id=revoked_by_user_id, incident_id=incident_id)

    def delete_session(self, session_secret: str):
        return self.revoke_session(session_secret)

    def delete_all_sessions(self, user_id: int):
        sessions = self.db.query(Sessions).filter(Sessions.user_id == user_id).all()
        for session in sessions:
            self.revoke_session_by_instance(session, revoked_by_user_id=session.user_id)
        return sessions

    def revoke_session_by_instance(self, session: Sessions, revoked_by_user_id: int | None = None, incident_id: int | None = None):
        ended_at = session.ended_at
        if ended_at.tzinfo is None:
            ended_at = ended_at.replace(tzinfo=timezone.utc)
        if ended_at <= datetime.now(timezone.utc):
            return session

        if revoked_by_user_id is None:
            revoked_by_user_id = session.user_id

        session.ended_at = datetime.now(timezone.utc)
        self.save(session, refresh=False)
        revocation = Revocations(
            incident_id=incident_id,
            target_session_id=session.id,
            revoked_by_user_id=revoked_by_user_id,
        )
        self.add_and_flush(revocation)
        return session