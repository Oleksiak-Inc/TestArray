from pydantic import BaseModel, ConfigDict
from typing import Optional

class ExecutionRelationshipCreate(BaseModel):
    execution_id: int
    related_execution_id: int
    relation_type_id: int

class ExecutionRelationshipOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    execution_id: int
    related_execution_id: int
    relation_type_id: int