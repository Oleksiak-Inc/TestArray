from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.scenario import *
from db.models.users import Users
from app.api.utils.users import get_current_user
from db.session import get_db
from app.services.scenario import ScenarioService

router = APIRouter(
    prefix="/scenarios",
    tags=["scenarios"],
)


@router.post("/", response_model=ScenarioOut, status_code=status.HTTP_201_CREATED)
def create_scenario(
    scenario_in: ScenarioCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = ScenarioService(db)
    return service.create_scenario(scenario_in.model_dump())


@router.get("/{scenario_id}", response_model=ScenarioOut)
def get_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    scenario = ScenarioService(db).get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.get("/", response_model=List[ScenarioOut])
def list_scenarios(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    return ScenarioService(db).list_scenarios()


@router.patch("/{scenario_id}", response_model=ScenarioOut)
def update_scenario(
    scenario_id: int,
    scenario_in: ScenarioUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    scenario = ScenarioService(db).update_scenario(
        scenario_id, scenario_in.model_dump(exclude_unset=True)
    )
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    scenario = ScenarioService(db).delete_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")