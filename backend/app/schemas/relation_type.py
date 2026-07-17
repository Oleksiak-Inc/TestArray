from pydantic import BaseModel, ConfigDict

class RelationTypeCreate(BaseModel):
    name: str

class RelationTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str