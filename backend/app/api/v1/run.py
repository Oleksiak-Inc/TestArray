from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.users import Users
from app.api.utils.auth_dependencies import get_current_user, get_current_admin_user, permission_required
from app.services.run import RunService
from app.schemas.run import *

router = APIRouter(
    prefix="/runs",
    tags=["runs"],
)


@router.post("/", response_model=RunOut, status_code=status.HTTP_201_CREATED)
def create_run(
    run_in: RunCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("runs.write")),
):
    service = RunService(db)
    run = service.create_run(run_in.model_dump())
    return run


@router.get("/{run_id}", response_model=RunOut, status_code=status.HTTP_200_OK)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("runs.read")),
):
    run = RunService(db).get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/project/{project_id}", response_model=List[RunOut])
def list_runs_by_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("runs.read")),
):
    runs = RunService(db).list_runs_by_project(project_id)
    return runs


@router.patch("/{run_id}", response_model=RunOut)
def update_run(
    run_id: int,
    run_in: RunUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("runs.write")),
):
    try:
        run = RunService(db).update_run(run_id, run_in.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.delete("/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    run = RunService(db).delete_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    


