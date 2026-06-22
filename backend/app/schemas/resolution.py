from pydantic import BaseModel, Field, ConfigDict

class ResolutionBase(BaseModel):
    w: int
    h: int

class ResolutionCreate(ResolutionBase):
    pass

class ResolutionUpdate(BaseModel):
    w: int | None = None
    h: int | None = None

class ResolutionOut(ResolutionBase):
    id: int
    w: int
    h: int

    model_config = ConfigDict(from_attributes=True)