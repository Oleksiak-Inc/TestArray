from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.group_permission import GroupPermissionCreate, GroupPermissionOut
from app.schemas.permission import PermissionOut
from db.models.users import Users
from app.api.utils.auth_dependencies import get_current_user, get_current_admin_user, permission_required
from db.session import get_db
from app.services.group_permission import GroupPermissionService

router = APIRouter(prefix="/group-permissions", tags=["group-permissions"])

@router.post("/", response_model=GroupPermissionOut, status_code=status.HTTP_201_CREATED)
def assign_permission(
    gp_in: GroupPermissionCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("group_permissions.write")),
):
    service = GroupPermissionService(db)
    try:
        gp = service.assign_permission(gp_in.group_id, gp_in.permission_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return gp

@router.delete("/{group_id}/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_permission(
    group_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("group_permissions.write")),
):
    service = GroupPermissionService(db)
    success = service.remove_permission(group_id, permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")

@router.get("/group/{group_id}", response_model=List[PermissionOut])
def list_permissions_for_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("group_permissions.read")),
):
    return GroupPermissionService(db).list_permissions_for_group(group_id)

@router.get("/permission/{permission_id}/groups", response_model=List[int])  # or List[UserGroupOut]
def list_groups_for_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("group_permissions.read")),
):
    groups = GroupPermissionService(db).list_groups_for_permission(permission_id)
    return [g.id for g in groups]  # or return full group objects if you add a schema