from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from db.session import get_db

from app.schemas.client import *
from app.schemas.project import *
from db.models.users import Users
from app.api.utils.http_errors import HttpError
from app.api.utils.auth_dependencies import permission_required

from app.services.project import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)

@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("projects.write")),
):
    service = ProjectService(db)
    project_data = project_in.model_dump()
    project_data["owner_id"] = current_user.id
    project = service.create_project(project_data)
    return project

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("projects.read")),
):
    project = ProjectService(db).get_project(project_id)
    if not project:
        HttpError.not_found("Project not found")
    return project

@router.get("/{project_id}/with-client", response_model=ProjectWithClient)
def get_project_with_client(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("projects.read")),
):
    project_with_client = ProjectService(db).get_project_with_client(project_id)
    if not project_with_client:
        HttpError.not_found("Project not found")
    return project_with_client

@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("projects.write")),
):
    project = ProjectService(db).update_project(project_id, project_in.model_dump(exclude_unset=True))
    if not project:
        HttpError.not_found("Project not found")
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("projects.write")),
):
    project = ProjectService(db).delete_project(project_id)
    if not project:
        HttpError.not_found("Project not found")