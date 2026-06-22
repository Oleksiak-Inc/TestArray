from pydantic import BaseModel, Field, ConfigDict
from app.schemas.project import ProjectOut

class ClientBase(BaseModel):
    name: str = Field(..., max_length=255)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)


class ClientOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ClientWithProjects(ClientOut):
    projects: list[ProjectOut]

    model_config = ConfigDict(from_attributes=True)