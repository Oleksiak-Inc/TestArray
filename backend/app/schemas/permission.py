from pydantic import BaseModel, ConfigDict, Field

class PermissionCreate(BaseModel):
    code: str = Field(..., max_length=100)
    description: str = Field(..., max_length=255)

class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    description: str