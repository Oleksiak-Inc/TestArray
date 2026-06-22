from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from db.session import get_db

from app.schemas.client import *
from db.models.clients import Clients
from db.models.projects import Projects
from db.models.users import Users
from app.api.utils.users import get_current_user, get_current_admin_user

from app.services.client import ClientService

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)

@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = ClientService(db)
    client = service.create_client(client_in.model_dump())
    return client

@router.get("/{client_id}", response_model=ClientOut)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    client = ClientService(db).get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.get("/{client_id}/with-projects", response_model=ClientWithProjects)
def get_client_with_projects(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    client_with_projects = ClientService(db).get_client_with_projects(client_id)
    if not client_with_projects:
        raise HTTPException(status_code=404, detail="Client not found")
    return client_with_projects

@router.patch("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    client_in: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    client = ClientService(db).update_client(client_id, client_in.model_dump(exclude_unset=True))
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    client = ClientService(db).delete_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
