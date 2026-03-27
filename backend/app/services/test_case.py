from sqlalchemy import text
from sqlalchemy.orm import joinedload

from db.models.test_cases import TestCases
from db.models.suitcases import Suitcases
from db.models.test_case_versions import TestCaseVersions
from app.services.suitcase import SuitcaseService

from utils.service import BaseService


class TestCaseService(BaseService):

    def get_test_case(self, test_case_id: int):
        return (
            self.db.query(TestCases)
            .filter(TestCases.id == test_case_id)
            .first()
        )

    def get_test_case_with_testsuites(self, test_case_id: int):
        return (
            self.db.query(TestCases)
            .filter(TestCases.id == test_case_id)
            .options(
                joinedload(TestCases.suitcases)
                .joinedload(Suitcases.test_suite)
            )
            .first()
        )

    def get_test_case_with_latest_version(self, test_case_id: int):

        result = self.db.execute(
            text("""
                SELECT DISTINCT ON (tc.id)
                    tc.id AS test_case_id,
                    tc.name AS test_case_name,
                    tcv.id AS version_id,
                    tcv.created_at,
                    tcv.release_ready
                FROM test_cases tc
                JOIN test_case_versions tcv
                    ON tcv.test_case_id = tc.id
                WHERE tc.id = :test_case_id
                  AND tcv.release_ready = true
                ORDER BY tc.id, tcv.created_at DESC
            """),
            {"test_case_id": test_case_id}
        ).fetchone()

        return result

    def get_test_case_with_all_versions(self, test_case_id: int):
        return (
            self.db.query(TestCases)
            .filter(TestCases.id == test_case_id)
            .options(
                joinedload(TestCases.versions)
            )
            .first()
        )

    def create_test_case(self, test_case_data):
        test_case = TestCases(**test_case_data)
        self.db.add(test_case)
        self.commit_and_refresh(test_case)
        return test_case
    
    def create_test_case_and_version(self, test_case_data, test_case_version_data, test_suite_id: int = None):
        test_case = TestCases(**test_case_data)
        self.db.add(test_case)
        self.db.flush()  # Get ID without committing
        test_case_version_data["test_case_id"] = test_case.id
        test_case_version = TestCaseVersions(**test_case_version_data)
        self.db.add(test_case_version)
        self.db.flush()

        if test_suite_id:
            suitcase_data = {
                "test_case_id": test_case.id,
                "test_suite_id": test_suite_id
            }
            suitcase = Suitcases(**suitcase_data)
            self.db.add(suitcase)

        self.db.commit()
        self.db.refresh(test_case)
        self.db.refresh(test_case_version)
        return test_case, test_case_version