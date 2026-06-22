from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class TestCaseBase(BaseModel):
    scenario_id: int
    status_set_id: int


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    scenario_id: Optional[int] = None
    status_set_id: Optional[int] = None


class TestCaseOut(TestCaseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class TestCaseWithVersionCreate(BaseModel):

    scenario_id: int
    status_set_id: int
    # Version fields (always version=1 for new test cases)
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    release_ready: bool = False
 
 
class TestCaseWithVersionOut(BaseModel):
    """What we return for each created item."""
    test_case_id: int
    test_case_version_id: int
    version: int
 
    model_config = ConfigDict(from_attributes=True)
 
 
class TestCaseBulkCreateIn(BaseModel):
    """Request body for POST /test-cases/bulk."""
    test_suite_id: Optional[int] = None
    test_cases: List[TestCaseWithVersionCreate] = Field(..., min_length=1)
 
 
class TestCaseBulkCreateOut(BaseModel):
    """Response body for POST /test-cases/bulk."""
    created: List[TestCaseWithVersionOut]
