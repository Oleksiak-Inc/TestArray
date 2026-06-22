from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.test_case import *
from db.models.users import Users
from app.api.utils.users import get_current_user
from db.session import get_db
from app.services.test_case import TestCaseService

router = APIRouter(
    prefix="/test-cases",
    tags=["test-cases"],
)


@router.post("/", response_model=TestCaseOut, status_code=status.HTTP_201_CREATED)
def create_test_case(
    test_case_in: TestCaseCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = TestCaseService(db)
    test_case = service.create_test_case(test_case_in.model_dump())
    return test_case


@router.post("/bulk", response_model=TestCaseBulkCreateOut, status_code=status.HTTP_201_CREATED)
def create_test_cases_bulk(
    bulk_in: TestCaseBulkCreateIn,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    items = [tc.model_dump() for tc in bulk_in.test_cases]
    results = TestCaseService(db).create_test_cases_and_versions_bulk(
        items=items,
        created_by=current_user.id,
        test_suite_id=bulk_in.test_suite_id,
    )
    return TestCaseBulkCreateOut(created=results)


@router.get("/{test_case_id}", response_model=TestCaseOut)
def get_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    test_case = TestCaseService(db).get_test_case(test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case


@router.get("/", response_model=List[TestCaseOut])
def list_test_cases(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = TestCaseService(db)
    test_cases = service.list_test_cases()
    return test_cases


@router.patch("/{test_case_id}", response_model=TestCaseOut)
def update_test_case(
    test_case_id: int,
    test_case_in: TestCaseUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    test_case = TestCaseService(db).update_test_case(test_case_id, test_case_in.model_dump(exclude_unset=True))
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case


@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    test_case = TestCaseService(db).delete_test_case(test_case_id)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")