from sqlalchemy.orm import Session
from app.schemas.auth import UserLogin, TokenPayload, UserLogout, UserRegister
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from typing import Optional
from datetime import datetime, timedelta
from app.schemas.users import UserOut
from app.api.utils.users import get_current_user
from db.session import get_db
from db.models.users import Users
from app.services.auth import AuthService
from core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/login", response_model=TokenPayload)
async def login(
    login_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    result = AuthService(db).login_user(
        email=login_data.email, 
        password=login_data.password
    )
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    response.set_cookie(
        key="session",
        value=result["access_token"],
        httponly=True,
        #secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_SECONDS
    )

    return TokenPayload(
        sub=result["user"].id,
        exp=int((datetime.utcnow() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)).timestamp())
    )

@router.post("/logout")
async def logout(
    response: Response,
    session: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    is_valid = AuthService(db).validate_session(session)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
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
        raise HTTPException(status_code=400, detail="User already exists")

    return UserOut(
        id=result.id,
        email=result.email,
        first_name=result.first_name,
        last_name=result.last_name,
        active=result.active,
        user_type_id=result.user_type_id,
        user_group_id=result.user_group_id,
        created_at=result.created_at,
        last_login_at=result.last_login_at
    )


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: Users = Depends(get_current_user),
):
    """Return the authenticated user's profile."""
    return current_user
    