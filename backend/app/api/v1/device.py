from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.device import *
from db.models.users import Users
from app.api.utils.users import get_current_user, get_current_admin_user
from db.session import get_db
from app.services.device import DeviceService

router = APIRouter(
    prefix="/devices",
    tags=["devices"],
)


@router.post("/", response_model=DeviceOut, status_code=status.HTTP_201_CREATED)
def create_device(
    device_in: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = DeviceService(db)
    device = service.create_device(device_in.model_dump())
    return device


@router.get("/{device_id}", response_model=DeviceOut)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    device = DeviceService(db).get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.get("/project/{project_id}", response_model=List[DeviceOut])
def list_devices_by_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    devices = DeviceService(db).list_devices_by_project(project_id)
    return devices


@router.patch("/{device_id}", response_model=DeviceOut)
def update_device(
    device_id: int,
    device_in: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    device = DeviceService(db).update_device(device_id, device_in.model_dump(exclude_unset=True))
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    device = DeviceService(db).delete_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")