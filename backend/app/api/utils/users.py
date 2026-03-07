from datetime import datetime

from fastapi import Depends, Cookie, HTTPException, status
from sqlalchemy.orm import Session

from app.services.session import SessionService
from app.services.users import UserService
from db.session import get_db


def get_current_user(
    session: str | None = Cookie(None),
    db: Session = Depends(get_db),
):
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session_obj = SessionService(db).get_session(session)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if session_obj.expires_at < datetime.utcnow():
        SessionService(db).delete_session(session)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    user = UserService(db).get_user_by_id(session_obj.user_id)
    if not user or not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return user
