from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.schemas.status import *
from db.models.users import Users
from app.api.utils.users import get_current_user, get_current_admin_user
from db.session import get_db
from app.services.status import StatusService

router = APIRouter(
    prefix="/status",
    tags=["status"],
)


@router.post("/", response_model=StatusOut, status_code=status.HTTP_201_CREATED)
def create_status(
    status_in: StatusCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = StatusService(db)
    return service.create_status(status_in.model_dump())


@router.get("/{status_id}", response_model=StatusOut)
def get_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    status_obj = StatusService(db).get_status(status_id)
    if not status_obj:
        raise HTTPException(status_code=404, detail="Status not found")
    return status_obj


@router.get("/", response_model=List[StatusOut])
def list_statuses(
    status_set_id: Optional[int] = Query(None, description="Filter by status set ID"),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = StatusService(db)
    if status_set_id is not None:
        return service.list_statuses_by_status_set(status_set_id)
    return service.list_all_statuses()


@router.patch("/{status_id}", response_model=StatusOut)
def update_status(
    status_id: int,
    status_in: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    status_obj = StatusService(db).update_status(
        status_id, status_in.model_dump(exclude_unset=True)
    )
    if not status_obj:
        raise HTTPException(status_code=404, detail="Status not found")
    return status_obj


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    status_obj = StatusService(db).delete_status(status_id)
    if not status_obj:
        raise HTTPException(status_code=404, detail="Status not found")