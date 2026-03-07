from pydantic import BaseModel, Field
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

    class Config:
        from_attributes = True


class ClientWithProjects(ClientOut):
    projects: list[ProjectOut]

    class Config:
        from_attributes = True