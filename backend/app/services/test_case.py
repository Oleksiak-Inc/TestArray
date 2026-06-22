from sqlalchemy import text
from sqlalchemy.orm import joinedload

from db.models.test_cases import TestCases
from db.models.suitcases import Suitcases
from db.models.test_case_versions import TestCaseVersions
from app.services.suitcase import SuitcaseService

from .utils.service import BaseService


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


    def create_test_cases_and_versions_bulk(
        self,
        items: list[dict],   # each dict: test_case_data + test_case_version_data merged
        created_by: int,
        test_suite_id: int = None,
    ) -> list[dict]:

        VERSION_FIELDS = {"name", "description", "steps", "expected_result", "release_ready"}
        TEST_CASE_FIELDS = {"scenario_id", "status_set_id"}
 
        results = []
 
        for item in items:
            # Split the flat dict into its two parts
            tc_data = {k: v for k, v in item.items() if k in TEST_CASE_FIELDS}
            tcv_data = {k: v for k, v in item.items() if k in VERSION_FIELDS}
 
            test_case = TestCases(**tc_data)
            self.db.add(test_case)
            self.db.flush()  # gives us test_case.id without committing yet
 
            tcv_data.update({
                "test_case_id": test_case.id,
                "created_by": created_by,
                "version": 1,
            })
            test_case_version = TestCaseVersions(**tcv_data)
            self.db.add(test_case_version)
            self.db.flush()
 
            if test_suite_id:
                self.db.add(Suitcases(
                    test_case_id=test_case.id,
                    test_suite_id=test_suite_id,
                ))
 
            results.append({
                "test_case_id": test_case.id,
                "test_case_version_id": test_case_version.id,
                "version": test_case_version.version,
            })
 
        # Single commit for the whole batch — all or nothing
        self.db.commit()
        return results

    
    def list_test_cases(self):
        return self.db.query(TestCases).all()

    def update_test_case(self, test_case_id: int, test_case_data):
        test_case = self.get_test_case(test_case_id)
        if not test_case:
            return None
        for key, value in test_case_data.items():
            setattr(test_case, key, value)
        self.commit_and_refresh(test_case)
        return test_case

    def delete_test_case(self, test_case_id: int):
        test_case = self.get_test_case(test_case_id)
        if not test_case:
            return None
        self.db.delete(test_case)
        self.db.commit()
        return test_case