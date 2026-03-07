from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from db.session import get_db

from app.schemas.client import ClientBase, ClientCreate, ClientOut, ClientUpdate, ClientWithProjects
from db.models.clients import Clients
from db.models.projects import Projects

from app.services.client import ClientService

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)

@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: ClientCreate,
    db: Session = Depends(get_db)
):
    service = ClientService(db)
    client = service.create_client(client_in.dict())
    return client
