from db.models.test_suites import TestSuites
from db.models.test_cases import TestCases
from db.models.suitcases import Suitcases
from db.models.test_case_versions import TestCaseVersions

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, text
from .utils.service import BaseService

class TestSuiteService(BaseService):
    def get_test_suite(self, test_suite_id: int):
        return self.db.query(TestSuites).filter(TestSuites.id == test_suite_id).first()
    
    def get_test_suite_with_test_cases(self, test_suite_id: int):
        return self.db.query(TestSuites).filter(TestSuites.id == test_suite_id).options(
            joinedload(TestSuites.suitcases).joinedload(Suitcases.test_case)
        ).first()
    
    def get_test_suite_with_test_cases_with_latest_test_case_version(self, test_suite_id: int):

        return (
            self.db.execute(
                text("""
                    SELECT DISTINCT ON (tc.id)
                        ts.id AS suite_id,
                        ts.name AS suite_name,
                        tc.id AS test_case_id,
                        tc.name AS test_case_name,
                        tcv.id AS version_id,
                        tcv.created_at
                    FROM test_suites ts
                    JOIN suitcases sc ON sc.test_suite_id = ts.id
                    JOIN test_cases tc ON tc.id = sc.test_case_id
                    JOIN test_case_versions tcv ON tcv.test_case_id = tc.id
                    WHERE ts.id = :test_suite_id
                    AND tcv.release_ready = true
                    ORDER BY tc.id, tcv.created_at DESC
                """),
                {"test_suite_id": test_suite_id}
            ).fetchall()
        )

    def create_test_suite(self, test_suite_data):
        test_suite = TestSuites(**test_suite_data)
        self.db.add(test_suite)
        self.commit_and_refresh(test_suite)
        return test_suite
    
    def update_test_suite(self, test_suite_id, test_suite_data):
        test_suite = self.get_test_suite(test_suite_id)
        if not test_suite:
            return None
        for key, value in test_suite_data.items():
            setattr(test_suite, key, value)
        self.commit_and_refresh(test_suite)
        return test_suite
    
