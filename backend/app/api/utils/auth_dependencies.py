from datetime import datetime, timezone
from typing import Optional

from fastapi import Cookie, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.utils.http_errors import HttpError
from app.services.session import SessionService
from app.services.users import UserService
from db.models.group_permissions import GroupPermissions
from db.models.groups_members import GroupsMembers
from db.models.permissions import Permissions
from db.models.user_types import UserTypes
from db.models.users import Users
from db.session import get_db


class AdminTypeCache:
    """Caches the 'admin' UserTypes.id at the class level (shared across
    requests/instances), not per-instance. UserTypes is reference data
    seeded once at startup (core/startup.py) and doesn't change at runtime,
    so this avoids a DB round trip on every authenticated request.
    """
    _admin_type_id: Optional[int] = None

    @classmethod
    def get(cls, db: Session) -> Optional[int]:
        if cls._admin_type_id is None:
            admin_type = db.query(UserTypes).filter(UserTypes.name == 'admin').first()
            cls._admin_type_id = admin_type.id if admin_type else None
        return cls._admin_type_id

    @classmethod
    def reset(cls) -> None:
        """Clear the cache. Call this in tests if you swap DBs/fixtures."""
        cls._admin_type_id = None


class PermissionChecker:
    def __init__(self, db: Session):
        self.db = db

    def is_admin(self, user: Users) -> bool:
        admin_type_id = AdminTypeCache.get(self.db)
        return admin_type_id is not None and user.user_type_id == admin_type_id

    def has_permission(self, user: Users, permission_code: str) -> bool:
        if not user:
            return False
        if self.is_admin(user):
            return True
        group_ids = select(GroupsMembers.group_id).where(GroupsMembers.user_id == user.id)
        return self.db.query(GroupPermissions).join(
            Permissions, GroupPermissions.permission_id == Permissions.id
        ).filter(
            GroupPermissions.group_id.in_(group_ids),
            Permissions.code == permission_code,
        ).first() is not None

    def require_permission(self, user: Users, permission_code: str) -> None:
        if not user or not self.has_permission(user, permission_code):
            HttpError.forbidden()


class SessionAuthenticator:
    def __init__(self, db: Session):
        self.db = db

    def resolve_user(self, session_secret: str) -> Users:
        session = SessionService(self.db).get_session(session_secret)
        if not session:
            HttpError.unauthorized()
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            SessionService(self.db).delete_session(session_secret)
            HttpError.unauthorized('Session expired')
        user = UserService(self.db).get_user_by_id(session.user_id)
        if not user or not user.active:
            HttpError.unauthorized()
        return user


def get_current_user(session: str | None = Cookie(None), db: Session = Depends(get_db)) -> Users:
    if not session:
        HttpError.unauthorized()
    return SessionAuthenticator(db).resolve_user(session)


async def get_current_admin_user(
    current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)
) -> Users:
    if not PermissionChecker(db).is_admin(current_user):
        HttpError.forbidden('Admin privileges required')
    return current_user


def permission_required(permission_code: str):
    def dependency(current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)) -> Users:
        PermissionChecker(db).require_permission(current_user, permission_code)
        return current_user
    return dependency