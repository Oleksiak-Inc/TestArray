from db.models.test_suites import TestSuites
from db.models.test_cases import TestCases
from db.models.suitcases import Suitcases
from db.models.test_case_versions import TestCaseVersions

from sqlalchemy.orm import Session, joinedload
from .utils.service import BaseService

class TestCaseVersionService(BaseService):
    def get_test_case_version(self, test_case_version_id: int):
        return self.db.query(TestCaseVersions).filter(TestCaseVersions.id == test_case_version_id).first()
    
    def get_test_case_version_with_test_case(self, test_case_version_id: int):
        return self.db.query(TestCaseVersions).filter(TestCaseVersions.id == test_case_version_id).options(
            joinedload(TestCaseVersions.test_case)
        ).first()
    
    def get_test_case_version_with_test_case_with_test_suites(self, test_case_version_id: int):
        return self.db.query(TestCaseVersions).filter(TestCaseVersions.id == test_case_version_id).options(
            joinedload(TestCaseVersions.test_case).joinedload(TestCases.suitcases).joinedload(Suitcases.test_suite)
        ).first()
    
    def get_test_case_version_by_test_case_id(self, test_case_id: int):
        return self.db.query(TestCaseVersions).filter(TestCaseVersions.test_case_id == test_case_id).first()
    
    def get_latest_release_ready_test_case_version_by_test_case_id(self, test_case_id: int):
        return self.db.query(TestCaseVersions).filter(
            TestCaseVersions.test_case_id == test_case_id,
            TestCaseVersions.release_ready == True
        ).order_by(TestCaseVersions.created_at.desc()).first()
    
    def create_test_case_version(self, test_case_version_data):
        test_case_version = TestCaseVersions(**test_case_version_data)
        self.db.add(test_case_version)
        self.commit_and_refresh(test_case_version)
        return test_case_version

    def list_test_case_versions_by_test_case(self, test_case_id: int):
        return self.db.query(TestCaseVersions).filter(TestCaseVersions.test_case_id == test_case_id).all()

    def update_test_case_version(self, test_case_version_id: int, test_case_version_data):
        test_case_version = self.get_test_case_version(test_case_version_id)
        if not test_case_version:
            return None
        for key, value in test_case_version_data.items():
            setattr(test_case_version, key, value)
        self.commit_and_refresh(test_case_version)
        return test_case_version

    def delete_test_case_version(self, test_case_version_id: int):
        test_case_version = self.get_test_case_version(test_case_version_id)
        if not test_case_version:
            return None
        self.db.delete(test_case_version)
        self.db.commit()
        return test_case_version