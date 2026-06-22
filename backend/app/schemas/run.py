from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class RunBase(BaseModel):
    name: str = Field(..., max_length=255)
    project_id: int


class RunCreate(RunBase):
    started_at: Optional[datetime] = None
    done_at: Optional[datetime] = None
    test_suite_metadata: Optional[str] = None


class RunUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    started_at: Optional[datetime] = None
    done_at: Optional[datetime] = None
    test_suite_metadata: Optional[str] = None


class RunOut(BaseModel):
    id: int
    name: str
    project_id: int
    started_at: Optional[datetime]
    done_at: Optional[datetime]
    test_suite_metadata: Optional[str]

    model_config = ConfigDict(from_attributes=True)