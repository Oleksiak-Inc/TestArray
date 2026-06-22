from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.test_suite import *
from db.models.users import Users
from app.api.utils.users import get_current_user, get_current_admin_user
from db.session import get_db
from app.services.test_suite import TestSuiteService

router = APIRouter(
    prefix="/test-suites",
    tags=["test-suites"],
)


@router.post("/", response_model=TestSuiteOut, status_code=status.HTTP_201_CREATED)
def create_test_suite(
    test_suite_in: TestSuiteCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = TestSuiteService(db)
    test_suite = service.create_test_suite(test_suite_in.model_dump())
    return test_suite


@router.get("/{test_suite_id}", response_model=TestSuiteOut)
def get_test_suite(
    test_suite_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    test_suite = TestSuiteService(db).get_test_suite(test_suite_id)
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return test_suite


@router.get("/", response_model=List[TestSuiteOut])
def list_test_suites(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = TestSuiteService(db)
    test_suites = service.list_test_suites()
    return test_suites


@router.get("/by-name/{name}", response_model=TestSuiteOut)
def get_test_suite_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    """Look up a test suite by its unique name.
 
    Returns 404 if no suite with that name exists, so the frontend can
    branch cleanly: found → use the id; not found → call POST /test-suites/.
    """
    test_suite = TestSuiteService(db).get_test_suite_by_name(name)
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return test_suite


@router.patch("/{test_suite_id}", response_model=TestSuiteOut)
def update_test_suite(
    test_suite_id: int,
    test_suite_in: TestSuiteUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    test_suite = TestSuiteService(db).update_test_suite(test_suite_id, test_suite_in.model_dump(exclude_unset=True))
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
    return test_suite


@router.delete("/{test_suite_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_suite(
    test_suite_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    test_suite = TestSuiteService(db).delete_test_suite(test_suite_id)
    if not test_suite:
        raise HTTPException(status_code=404, detail="Test suite not found")