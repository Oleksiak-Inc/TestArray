from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user_group import *
from db.models.users import Users
from app.api.utils.users import get_current_user
from db.session import get_db
from app.services.user_group import UserGroupService

router = APIRouter(
    prefix="/user-groups",
    tags=["user-groups"],
)


@router.post("/", response_model=UserGroupOut, status_code=status.HTTP_201_CREATED)
def create_user_group(
    group_in: UserGroupCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = UserGroupService(db)
    # Auto-set created_by_id to the current user
    data = group_in.model_dump()
    data["created_by_id"] = current_user.id
    return service.create_user_group(data)


@router.get("/{group_id}", response_model=UserGroupOut)
def get_user_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    group = UserGroupService(db).get_user_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="User group not found")
    return group


@router.get("/", response_model=List[UserGroupOut])
def list_user_groups(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return UserGroupService(db).list_user_groups()


@router.patch("/{group_id}", response_model=UserGroupOut)
def update_user_group(
    group_id: int,
    group_in: UserGroupUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    group = UserGroupService(db).update_user_group(
        group_id, group_in.model_dump(exclude_unset=True)
    )
    if not group:
        raise HTTPException(status_code=404, detail="User group not found")
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    group = UserGroupService(db).delete_user_group(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="User group not found")