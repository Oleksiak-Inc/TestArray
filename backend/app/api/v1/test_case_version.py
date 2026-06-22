from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.test_case_version import *
from db.models.users import Users
from app.api.utils.users import get_current_user
from db.session import get_db
from app.services.test_case_version import TestCaseVersionService

router = APIRouter(
    prefix="/test-case-versions",
    tags=["test-case-versions"],
)


@router.post("/", response_model=TestCaseVersionOut, status_code=status.HTTP_201_CREATED)
def create_test_case_version(
    test_case_version_in: TestCaseVersionCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = TestCaseVersionService(db)
    test_case_version = service.create_test_case_version(test_case_version_in.model_dump())
    return test_case_version


@router.get("/{test_case_version_id}", response_model=TestCaseVersionOut)
def get_test_case_version(
    test_case_version_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    test_case_version = TestCaseVersionService(db).get_test_case_version(test_case_version_id)
    if not test_case_version:
        raise HTTPException(status_code=404, detail="Test case version not found")
    return test_case_version


@router.get("/test-case/{test_case_id}", response_model=List[TestCaseVersionOut])
def list_test_case_versions_by_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = TestCaseVersionService(db)
    test_case_versions = service.list_test_case_versions_by_test_case(test_case_id)
    return test_case_versions


@router.patch("/{test_case_version_id}", response_model=TestCaseVersionOut)
def update_test_case_version(
    test_case_version_id: int,
    test_case_version_in: TestCaseVersionUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    test_case_version = TestCaseVersionService(db).update_test_case_version(test_case_version_id, test_case_version_in.model_dump(exclude_unset=True))
    if not test_case_version:
        raise HTTPException(status_code=404, detail="Test case version not found")
    return test_case_version


@router.delete("/{test_case_version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case_version(
    test_case_version_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    test_case_version = TestCaseVersionService(db).delete_test_case_version(test_case_version_id)
    if not test_case_version:
        raise HTTPException(status_code=404, detail="Test case version not found")