from datetime import datetime, timezone

from fastapi import Depends, Cookie, HTTPException, status
from sqlalchemy.orm import Session

from app.services.session import SessionService
from app.services.users import UserService
from db.session import get_db

from db.models.users import Users
from db.models.user_types import UserTypes


def get_current_user(
    session: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )

    session_obj = SessionService(db).get_session(session)
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )

    expires_at = session_obj.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        SessionService(db).delete_session(session)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Session expired"
        )

    user = UserService(db).get_user_by_id(session_obj.user_id)
    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )

    return user

async def get_current_admin_user(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Users:
    admin_type = db.query(UserTypes).filter(UserTypes.name == "admin").first()
    if not admin_type or current_user.user_type_id != admin_type.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
