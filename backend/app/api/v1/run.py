from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from db.session import get_db
from db.models.users import Users
from app.api.utils.users import get_current_user
from app.services.run import RunService

router = APIRouter(
    prefix="/runs",
    tags=["runs"],
)

@router.get("/{run_id}", status_code=status.HTTP_200_OK)
def get_runs(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    run = RunService(db).get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
    


