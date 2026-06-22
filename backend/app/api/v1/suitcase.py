from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.suitcase import *
from db.models.users import Users
from app.api.utils.users import get_current_user, get_current_admin_user
from db.session import get_db
from app.services.suitcase import SuitcaseService
from db.models.test_cases import TestCases
from db.models.test_suites import TestSuites

router = APIRouter(
    prefix="/suitcases",
    tags=["suitcases"],
)


@router.post("/", response_model=SuitcaseOut, status_code=status.HTTP_201_CREATED)
def create_suitcase(
    suitcase_in: SuitcaseCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    service = SuitcaseService(db)
    suitcase = service.create_suitcase(suitcase_in.model_dump())
    return suitcase

@router.post("/bulk", response_model=SuitcaseBulkCreateOut, status_code=status.HTTP_201_CREATED)
def create_suitcases_bulk(
    bulk_in: SuitcaseBulkCreateIn,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    # Validate suite exists
    suite = db.query(TestSuites).filter(TestSuites.id == bulk_in.test_suite_id).first()
    if not suite:
        raise HTTPException(status_code=404, detail="Test suite not found")
 
    # Validate all test case ids exist
    found_ids = {
        row.id
        for row in db.query(TestCases.id)
        .filter(TestCases.id.in_(bulk_in.test_case_ids))
        .all()
    }
    missing = set(bulk_in.test_case_ids) - found_ids
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Test cases not found: {sorted(missing)}",
        )
 
    result = SuitcaseService(db).create_suitcases_bulk(
        test_suite_id=bulk_in.test_suite_id,
        test_case_ids=bulk_in.test_case_ids,
    )
    return SuitcaseBulkCreateOut(**result)

@router.get("/{suitcase_id}", response_model=SuitcaseOut)
def get_suitcase(
    suitcase_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    suitcase = SuitcaseService(db).get_suitcase(suitcase_id)
    if not suitcase:
        raise HTTPException(status_code=404, detail="Suitcase not found")
    return suitcase


@router.get("/test-case/{test_case_id}", response_model=List[SuitcaseOut])
def list_suitcases_by_test_case(
    test_case_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    suitcases = SuitcaseService(db).get_suitcases_by_test_case_id(test_case_id)
    return suitcases


@router.get("/test-suite/{test_suite_id}", response_model=List[SuitcaseOut])
def list_suitcases_by_test_suite(
    test_suite_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    suitcases = SuitcaseService(db).get_suitcases_by_test_suite_id(test_suite_id)
    return suitcases


@router.patch("/{suitcase_id}", response_model=SuitcaseOut)
def update_suitcase(
    suitcase_id: int,
    suitcase_in: SuitcaseUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user),
):
    suitcase = SuitcaseService(db).update_suitcase(suitcase_id, suitcase_in.model_dump(exclude_unset=True))
    if not suitcase:
        raise HTTPException(status_code=404, detail="Suitcase not found")
    return suitcase


@router.delete("/{suitcase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_suitcase(
    suitcase_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_admin_user),
):
    suitcase = SuitcaseService(db).delete_suitcase(suitcase_id)
    if not suitcase:
        raise HTTPException(status_code=404, detail="Suitcase not found")