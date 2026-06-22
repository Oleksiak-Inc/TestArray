from sqlalchemy import text
from sqlalchemy.orm import joinedload

from db.models.test_cases import TestCases
from db.models.suitcases import Suitcases
from db.models.test_case_versions import TestCaseVersions

from .utils.service import BaseService


class SuitcaseService(BaseService):

    def create_suitcase(self, suitcase_data: dict) -> Suitcases:
        suitcase = Suitcases(**suitcase_data)
        self.db.add(suitcase)
        self.commit_and_refresh(suitcase)
        return suitcase

    def create_suitcases_bulk(
        self,
        test_suite_id: int,
        test_case_ids: list[int],
    ) -> dict:
        # Fetch already-linked test case ids for this suite in one query
        existing_ids = {
            row.test_case_id
            for row in self.db.query(Suitcases.test_case_id)
            .filter(
                Suitcases.test_suite_id == test_suite_id,
                Suitcases.test_case_id.in_(test_case_ids),
            )
            .all()
        }
 
        created = []
        skipped = []
 
        for tc_id in test_case_ids:
            if tc_id in existing_ids:
                skipped.append(tc_id)
                continue
            suitcase = Suitcases(test_case_id=tc_id, test_suite_id=test_suite_id)
            self.db.add(suitcase)
            self.db.flush()   # gives us suitcase.id before commit
            created.append(suitcase)
 
        self.db.commit()
        for s in created:
            self.db.refresh(s)
 
        return {"created": created, "skipped_duplicate_test_case_ids": skipped}

    def get_suitcase(self, suitcase_id: int):
        return self.db.query(Suitcases).filter(Suitcases.id == suitcase_id).first()
    
    def get_suitcases_by_test_case_id(self, test_case_id: int):
        return self.db.query(Suitcases).filter(Suitcases.test_case_id == test_case_id).all()
    
    def get_suitcases_by_test_suite_id(self, test_suite_id: int):
        return self.db.query(Suitcases).filter(Suitcases.test_suite_id == test_suite_id).all()
    
    def get_suitcases_by_test_case_and_test_suite_id(self, test_case_id: int, test_suite_id: int):
        return self.db.query(Suitcases).filter(
            Suitcases.test_case_id == test_case_id,
            Suitcases.test_suite_id == test_suite_id
        ).all()
    
    def update_suitcase(self, suitcase_id: int, suitcase_data):
        suitcase = self.get_suitcase(suitcase_id)
        if not suitcase:
            return None
        for key, value in suitcase_data.items():
            setattr(suitcase, key, value)
        self.commit_and_refresh(suitcase)
        return suitcase

    def delete_suitcase(self, suitcase_id: int):
        suitcase = self.get_suitcase(suitcase_id)
        if not suitcase:
            return None
        self.db.delete(suitcase)
        self.db.commit()
        return suitcase