from pydantic import BaseModel, Field

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

    class Config:
        from_attributes = True