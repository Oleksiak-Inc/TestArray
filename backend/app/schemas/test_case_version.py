from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TestCaseVersionBase(BaseModel):
    test_case_id: int
    version: int
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    release_ready: bool = False


class TestCaseVersionCreate(TestCaseVersionBase):
    created_by: int


class TestCaseVersionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    release_ready: Optional[bool] = None


class TestCaseVersionOut(TestCaseVersionBase):
    id: int
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
