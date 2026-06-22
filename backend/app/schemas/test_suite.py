from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TestSuiteBase(BaseModel):
    name: str = Field(..., max_length=255)


class TestSuiteCreate(TestSuiteBase):
    pass


class TestSuiteUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)


class TestSuiteOut(TestSuiteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
