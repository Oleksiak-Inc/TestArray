from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.execution_relationship import ExecutionRelationshipCreate, ExecutionRelationshipOut
from db.session import get_db
from app.api.utils.auth_dependencies import permission_required
from db.models.users import Users
from app.services.execution_relationship import ExecutionRelationshipService

router = APIRouter(prefix="/execution-relationships", tags=["execution-relationships"])

@router.post("/", response_model=ExecutionRelationshipOut, status_code=status.HTTP_201_CREATED)
def create_relationship(
    rel_in: ExecutionRelationshipCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("execution_relationships.write")),
):
    service = ExecutionRelationshipService(db)
    rel = service.create_relationship(
        execution_id=rel_in.execution_id,
        related_execution_id=rel_in.related_execution_id,
        relation_type_id=rel_in.relation_type_id,
    )
    return rel

@router.get("/execution/{execution_id}", response_model=list[ExecutionRelationshipOut])
def list_relationships(
    execution_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("execution_relationships.read")),
):
    service = ExecutionRelationshipService(db)
    return service.get_relationships_for_execution(execution_id)

@router.delete("/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(
    relationship_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(permission_required("execution_relationships.write")),
):
    service = ExecutionRelationshipService(db)
    success = service.delete_relationship(relationship_id)
    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found")