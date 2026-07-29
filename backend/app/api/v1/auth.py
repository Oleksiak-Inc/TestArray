from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Response, Request
from sqlalchemy.orm import Session

from app.api.utils.auth_dependencies import get_current_user, permission_required
from app.api.utils.http_errors import HttpError
from app.schemas.auth import *
from app.schemas.users import UserOut
from app.services.auth import AuthService
from app.services.session import SessionService
from core.config import settings
from core.security_tokens import SessionTokenFactory
from db.models.groups_members import GroupsMembers
from db.models.group_permissions import GroupPermissions
from db.models.incidents import Incidents
from db.models.permissions import Permissions
from db.models.revocations import Revocations
from db.models.sessions import Sessions
from db.models.user_groups import UserGroups
from db.models.users import Users
from db.session import get_db


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/login", response_model=TokenPayload)
async def login(
    login_data: UserLogin,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    result = AuthService(db).login_user(
        email=login_data.email,
        password=login_data.password,
        request=request,
    )
    if not result:
        HttpError.unauthorized("Invalid credentials")

    secure = settings.SECURE_COOKIES

    response.set_cookie(
        key="session",
        value=result["access_token"],
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS
    )

    return TokenPayload(
        sub=result["user"].id,
        exp=int(result["expires_at"]),
    )

@router.post("/logout")
async def logout(
    response: Response,
    session: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    if not session:
        HttpError.unauthorized()

    is_valid = AuthService(db).validate_session(session)
    if not is_valid:
        HttpError.unauthorized()
    
    AuthService(db).logout_user(session)

    response.delete_cookie(key="session")
    return UserLogout()
    
@router.post("/register", response_model=UserOut)
async def register(
    login_data: UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):
    result = AuthService(db).register_user(
        first_name=login_data.first_name,
        last_name=login_data.last_name,
        email=login_data.email, 
        password=login_data.password
    )
    if not result:
        HttpError.bad_request('User already exists')

    return UserOut(
        id=result.id,
        email=result.email,
        first_name=result.first_name,
        last_name=result.last_name,
        active=result.active,
        created_at=result.created_at,
        last_login_at=result.last_login_at
    )


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: Users = Depends(get_current_user),
):
    """Return the authenticated user's profile."""
    return current_user


@router.get("/sessions")
def list_user_sessions(
    session: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    sessions = SessionService(db).get_active_sessions_for_user(current_user.id)
    current_hash = SessionTokenFactory.hash_secret(session) if session else None
    return [{
        "id": session_obj.id,
        "created_at": session_obj.created_at,
        "expires_at": session_obj.expires_at,
        "ended_at": session_obj.ended_at,
        "user_agent": session_obj.user_agent,
        "ip_address": session_obj.ip_address,
        "is_current": current_hash is not None and session_obj.token == current_hash,
    } for session_obj in sessions]


@router.delete("/sessions/{session_id}")
def revoke_own_session(
    session_id: int,
    response: Response,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    session = db.query(Sessions).filter(Sessions.id == session_id, Sessions.user_id == current_user.id).first()
    if not session:
        HttpError.not_found("Session not found")
    SessionService(db).revoke_session_by_instance(session, revoked_by_user_id=current_user.id)
    response.status_code = 200
    return {"message": "Session revoked"}


@router.delete("/sessions")
def revoke_all_other_sessions(
    keep_current: bool = True,
    response: Response = None,
    session: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    sessions = db.query(Sessions).filter(
        Sessions.user_id == current_user.id,
        Sessions.ended_at > datetime.now(timezone.utc),
    ).all()
    current_hash = SessionTokenFactory.hash_secret(session) if session and keep_current else None
    for session_obj in sessions:
        if current_hash and session_obj.token == current_hash:
            continue
        SessionService(db).revoke_session_by_instance(session_obj, revoked_by_user_id=current_user.id)
    return {"message": "Sessions revoked"}


@router.delete("/admin/sessions/{session_id}")
def admin_revoke_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("sessions.delete")),
):
    session = db.query(Sessions).filter(Sessions.id == session_id).first()
    if not session:
        HttpError.not_found("Session not found")

    incident = Incidents(
        triggered_by_user_id=current_user.id,
        target_user_id=session.user_id,
        category="session",
        severity="high",
        description="Admin revoked a user session",
    )
    db.add(incident)
    db.flush()
    SessionService(db).revoke_session_by_instance(session, revoked_by_user_id=current_user.id, incident_id=incident.id)
    return {"message": "Session revoked"}


@router.get("/context")
async def get_application_context(
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the authorization data needed to assemble the frontend workspaces."""
    groups = db.query(UserGroups).join(
        GroupsMembers, GroupsMembers.group_id == UserGroups.id
    ).filter(GroupsMembers.user_id == current_user.id).all()

    group_ids = db.query(GroupsMembers.group_id).filter(GroupsMembers.user_id == current_user.id)
    permission_query = (
        db.query(Permissions.code)
        .join(GroupPermissions, GroupPermissions.permission_id == Permissions.id)
        .filter(GroupPermissions.group_id.in_(group_ids))
        .distinct()
    )

    return {
        "user": UserOut.model_validate(current_user).model_dump(mode="json"),
        "groups": [{"id": group.id, "name": group.name} for group in groups],
        "permissions": [code for (code,) in permission_query.all()],
        "is_admin": False,
    }
