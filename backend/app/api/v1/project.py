from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from db.session import get_db

from app.schemas.client import ClientBase, ClientCreate, ClientOut, ClientUpdate, ClientWithProjects
from app.schemas.project import ProjectBase, ProjectCreate, ProjectOut, ProjectUpdate, ProjectWithClient
from db.models.clients import Clients
from db.models.projects import Projects
from db.models.users import Users
from app.api.utils.users import get_current_user

from app.services.project import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)

@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = ProjectService(db)
    project = service.create_project(project_in.dict())
    return project

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    project = ProjectService(db).get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/with-client", response_model=ProjectWithClient)
def get_project_with_client(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    project_with_client = ProjectService(db).get_project_with_client(project_id)
    if not project_with_client:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_with_client

@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    project = ProjectService(db).update_project(project_id, project_in.dict(exclude_unset=True))
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project