from pydantic import BaseModel, Field, ConfigDict

class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255)
    client_id: int

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    client_id: int | None = None

class ProjectOut(ProjectBase):
    id: int
    name: str
    client_id: int

    model_config = ConfigDict(from_attributes=True)

class ProjectWithClient(ProjectOut):
    client_id: int

    model_config = ConfigDict(from_attributes=True)