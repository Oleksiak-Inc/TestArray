from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.status_set import *
from db.models.users import Users
from app.api.utils.users import get_current_user, get_current_admin_user
from db.session import get_db
from app.services.status_set import StatusSetService

router = APIRouter(
    prefix="/status-sets",
    tags=["status-sets"],
)


@router.post("/", response_model=StatusSetOut, status_code=status.HTTP_201_CREATED)
def create_status_set(
    status_set_in: StatusSetCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = StatusSetService(db)
    return service.create_status_set(status_set_in.model_dump())


@router.get("/{status_set_id}", response_model=StatusSetOut)
def get_status_set(
    status_set_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    status_set = StatusSetService(db).get_status_set(status_set_id)
    if not status_set:
        raise HTTPException(status_code=404, detail="Status set not found")
    return status_set


@router.get("/", response_model=List[StatusSetOut])
def list_status_sets(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return StatusSetService(db).list_status_sets()


@router.patch("/{status_set_id}", response_model=StatusSetOut)
def update_status_set(
    status_set_id: int,
    status_set_in: StatusSetUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    status_set = StatusSetService(db).update_status_set(
        status_set_id, status_set_in.model_dump(exclude_unset=True)
    )
    if not status_set:
        raise HTTPException(status_code=404, detail="Status set not found")
    return status_set


@router.delete("/{status_set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status_set(
    status_set_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    status_set = StatusSetService(db).delete_status_set(status_set_id)
    if not status_set:
        raise HTTPException(status_code=404, detail="Status set not found")