from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.utils.users import get_current_admin_user, get_current_user
from app.schemas.execution import ExecutionCreate, ExecutionOut, ExecutionUpdate
from app.services.execution import ExecutionService
from db.models.users import Users
from db.session import get_db

router = APIRouter(
    prefix="/executions",
    tags=["executions"],
)


@router.post("/matrix", response_model=List[ExecutionOut], status_code=status.HTTP_201_CREATED)
def create_execution_matrix(
    execution_in: ExecutionCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = ExecutionService(db)
    try:
        executions = service.create_executions_for_test_suite(
            test_suite_id=execution_in.test_suite_id,
            run_id=execution_in.run_id,
            device_ids=execution_in.device_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return executions


@router.get("/{execution_id}", response_model=ExecutionOut)
def get_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    execution = ExecutionService(db).get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.get("/run/{run_id}", response_model=List[ExecutionOut])
def list_executions_by_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return ExecutionService(db).list_executions_by_run(run_id)


@router.patch("/{execution_id}", response_model=ExecutionOut)
def update_execution(
    execution_id: int,
    execution_in: ExecutionUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = ExecutionService(db)
    try:
        execution = service.update_execution(
            execution_id,
            execution_in.model_dump(exclude_unset=True),
            current_user,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_execution(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    execution = ExecutionService(db).delete_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")