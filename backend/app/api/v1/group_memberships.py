from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.group_membership import GroupMembershipCreate, GroupMembershipOut
from app.schemas.users import UserOut
from app.schemas.user_group import UserGroupOut
from db.session import get_db
from app.api.utils.auth_dependencies import get_current_user, get_current_admin_user, permission_required
from db.models.users import Users
from app.services.group_membership import GroupMembershipService

router = APIRouter(prefix="/group-memberships", tags=["group-memberships"])

@router.post("/", response_model=GroupMembershipOut, status_code=status.HTTP_201_CREATED)
def add_member(
    membership_in: GroupMembershipCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("group_memberships.write")),
):
    service = GroupMembershipService(db)
    try:
        membership = service.add_member(membership_in.group_id, membership_in.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return membership

@router.delete("/{group_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    service = GroupMembershipService(db)
    try:
        success = service.remove_member(group_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not success:
        raise HTTPException(status_code=404, detail="Membership not found")

@router.get("/group/{group_id}/members", response_model=list[UserOut])
def list_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("group_memberships.read")),
):
    service = GroupMembershipService(db)
    members = service.list_group_members(group_id)
    return members

@router.get("/user/{user_id}/groups", response_model=list[UserGroupOut])
def list_user_groups(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("group_memberships.read")),
):
    service = GroupMembershipService(db)
    groups = service.list_user_groups(user_id)
    return groups