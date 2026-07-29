from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.permission import PermissionCreate, PermissionOut
from db.models.users import Users
from app.api.utils.auth_dependencies import permission_required
from db.session import get_db
from app.services.permission import PermissionService

router = APIRouter(prefix="/permissions", tags=["permissions"])

@router.get("/", response_model=List[PermissionOut])
def list_permissions(
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("permissions.read")),
):
    return PermissionService(db).list_permissions()

@router.post("/", response_model=PermissionOut, status_code=status.HTTP_201_CREATED)
def create_permission(
    perm_in: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("permissions.write")),
):
    service = PermissionService(db)
    # Check for duplicate code
    if service.get_permission_by_code(perm_in.code):
        raise HTTPException(status_code=400, detail="Permission code already exists")
    return service.create_permission(perm_in.model_dump())

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("permissions.delete")),
):
    perm = PermissionService(db).delete_permission(permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")