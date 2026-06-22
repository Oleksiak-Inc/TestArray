from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.resolution import *
from db.models.users import Users
from app.api.utils.users import get_current_user, get_current_admin_user
from db.session import get_db
from app.services.resolution import ResolutionService

router = APIRouter(
    prefix="/resolutions",
    tags=["resolutions"],
)


@router.post("/", response_model=ResolutionOut, status_code=status.HTTP_201_CREATED)
def create_resolution(
    resolution_in: ResolutionCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = ResolutionService(db)
    return service.create_resolution(resolution_in.model_dump())


@router.get("/{resolution_id}", response_model=ResolutionOut)
def get_resolution(
    resolution_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    resolution = ResolutionService(db).get_resolution(resolution_id)
    if not resolution:
        raise HTTPException(status_code=404, detail="Resolution not found")
    return resolution


@router.get("/", response_model=List[ResolutionOut])
def list_resolutions(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return ResolutionService(db).list_resolutions()


@router.patch("/{resolution_id}", response_model=ResolutionOut)
def update_resolution(
    resolution_id: int,
    resolution_in: ResolutionUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    resolution = ResolutionService(db).update_resolution(
        resolution_id, resolution_in.model_dump(exclude_unset=True)
    )
    if not resolution:
        raise HTTPException(status_code=404, detail="Resolution not found")
    return resolution


@router.delete("/{resolution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resolution(
    resolution_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    resolution = ResolutionService(db).delete_resolution(resolution_id)
    if not resolution:
        raise HTTPException(status_code=404, detail="Resolution not found")