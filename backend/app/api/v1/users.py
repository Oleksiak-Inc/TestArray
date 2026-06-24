from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.users import *
from db.models.users import Users
from app.api.utils.users import get_current_user, get_current_admin_user
from db.session import get_db
from app.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# ---- Admin-only endpoints ----
@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    """List all users (admin only)."""
    return UserService(db).list_users()

# ---- Self-service endpoints ----

@router.patch("/me", response_model=UserOut)
def update_self(
    user_in: UserUpdateSelf,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Authenticated user updates their own profile."""
    # Prevent email conflicts
    if user_in.email and user_in.email != current_user.email:
        existing = UserService(db).get_user_by_email(user_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
    user = UserService(db).update_user(current_user.id, user_in.model_dump(exclude_unset=True))
    return user


@router.get("/me", response_model=UserOut)
def get_self(
    current_user: Users = Depends(get_current_user),
):
    """Get current user profile (convenience duplicate of /auth/me)."""
    return current_user

# ---- Admin-only endpoints for specific users ----

@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    """Get a user by ID (admin only)."""
    user = UserService(db).get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def admin_update_user(
    user_id: int,
    user_in: UserUpdateAdmin,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    """Admin updates user fields (group, type, active)."""
    user = UserService(db).update_user(user_id, user_in.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    """Delete a user (admin only)."""
    user = UserService(db).delete_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


