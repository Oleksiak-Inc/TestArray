from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class SuitcaseBase(BaseModel):
    test_case_id: int
    test_suite_id: int


class SuitcaseCreate(SuitcaseBase):
    pass


class SuitcaseUpdate(BaseModel):
    test_case_id: Optional[int] = None
    test_suite_id: Optional[int] = None


class SuitcaseOut(SuitcaseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class SuitcaseBulkCreateIn(BaseModel):
    test_suite_id: int
    test_case_ids: List[int] = Field(..., min_length=1)
 
 
class SuitcaseBulkCreateOut(BaseModel):
    created: List[SuitcaseOut]
    skipped_duplicate_test_case_ids: List[int]