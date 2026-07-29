from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.relation_type import RelationTypeCreate, RelationTypeOut
from db.models.users import Users
from app.api.utils.auth_dependencies import permission_required
from db.session import get_db
from app.services.relation_type import RelationTypeService

router = APIRouter(
    prefix="/relation-types",
    tags=["relation-types"],
)

@router.post("/", response_model=RelationTypeOut, status_code=status.HTTP_201_CREATED)
def create_relation_type(
    type_in: RelationTypeCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("relation_types.write")),
):
    service = RelationTypeService(db)
    return service.create_relation_type(type_in.model_dump())

@router.get("/", response_model=List[RelationTypeOut])
def list_relation_types(
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("relation_types.read")),
):
    service = RelationTypeService(db)
    return service.list_relation_types()

@router.get("/{type_id}", response_model=RelationTypeOut)
def get_relation_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("relation_types.read")),
):
    service = RelationTypeService(db)
    rel_type = service.get_relation_type(type_id)
    if not rel_type:
        raise HTTPException(status_code=404, detail="Relation type not found")
    return rel_type

@router.patch("/{type_id}", response_model=RelationTypeOut)
def update_relation_type(
    type_id: int,
    type_in: RelationTypeCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("relation_types.write")),
):
    service = RelationTypeService(db)
    rel_type = service.update_relation_type(type_id, type_in.model_dump())
    if not rel_type:
        raise HTTPException(status_code=404, detail="Relation type not found")
    return rel_type

@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relation_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("relation_types.write")),
):
    service = RelationTypeService(db)
    rel_type = service.delete_relation_type(type_id)
    if not rel_type:
        raise HTTPException(status_code=404, detail="Relation type not found")