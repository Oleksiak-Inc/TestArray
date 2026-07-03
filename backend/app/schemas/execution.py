from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExecutionBase(BaseModel):
    device_id: int
    run_id: int
    test_case_version_id: int
    status_id: Optional[int] = None
    attachment_id: Optional[int] = None
    resolution_id: Optional[int] = None
    actual_result: Optional[str] = None
    execution_order: int


class ExecutionCreate(BaseModel):
    test_suite_id: int
    run_id: int
    device_ids: list[int] = Field(..., min_length=1)


class ExecutionUpdate(BaseModel):
    status_id: Optional[int] = None
    attachment_id: Optional[int] = None
    resolution_id: Optional[int] = None
    actual_result: Optional[str] = None


class ExecutionOut(ExecutionBase):
    id: int
    executed_by: Optional[int] = None
    updated_by: Optional[int] = None
    executed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
