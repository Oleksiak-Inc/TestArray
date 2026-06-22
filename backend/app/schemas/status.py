from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class StatusBase(BaseModel):
    status_set_id: int
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class StatusCreate(StatusBase):
    pass


class StatusUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class StatusOut(StatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)