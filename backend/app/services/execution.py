from datetime import datetime, timezone
from typing import Any

from db.models.attachments import Attachments
from db.models.devices import Devices
from db.models.executions import Executions
from db.models.resolutions import Resolutions
from db.models.runs import Runs
from db.models.statuses import Statuses
from db.models.suitcases import Suitcases
from db.models.test_suites import TestSuites
from db.models.users import Users
from app.services.test_case_version import TestCaseVersionService
from .utils.service import BaseService


class ExecutionService(BaseService):
    def get_execution(self, execution_id: int):
        return self.get_by_id(Executions, execution_id)

    def list_executions(self):
        return self.db.query(Executions).all()

    def list_executions_by_run(self, run_id: int):
        return self.db.query(Executions).filter(Executions.run_id == run_id).all()

    def _get_latest_test_case_version(self, test_case_id: int):
        return TestCaseVersionService(self.db).get_latest_test_case_version_by_test_case_id(test_case_id)

    def create_executions_for_test_suite(self, *, test_suite_id: int, run_id: int, device_ids: list[int]):
        test_suite = self.db.query(TestSuites).filter(TestSuites.id == test_suite_id).first()
        if not test_suite:
            raise ValueError("Test suite not found")

        run = self.db.query(Runs).filter(Runs.id == run_id).first()
        if not run:
            raise ValueError("Run not found")

        devices = self.db.query(Devices).filter(Devices.id.in_(device_ids)).all()
        if len(device_ids) != len(set(device_ids)):
            raise ValueError("Duplicate device IDs are not allowed")
        if len(devices) != len(set(device_ids)):
            raise ValueError("One or more devices were not found")

        for device in devices:
            if device.project_id != run.project_id:
                raise ValueError("Device does not belong to the selected run project")

        suitcases = (
            self.db.query(Suitcases)
            .filter(Suitcases.test_suite_id == test_suite_id)
            .order_by(Suitcases.id)
            .all()
        )
        if not suitcases:
            raise ValueError("The selected test suite has no test cases")

        created: list[Executions] = []
        execution_order = 1

        for suitcase in suitcases:
            version = self._get_latest_test_case_version(suitcase.test_case_id)
            if not version:
                raise ValueError(f"Test case {suitcase.test_case_id} has no version available")

            for device in devices:
                existing = self.get_one(
                    Executions,
                    run_id=run_id,
                    device_id=device.id,
                    test_case_version_id=version.id,
                )
                if existing:
                    continue

                execution = Executions(
                    device_id=device.id,
                    run_id=run_id,
                    test_case_version_id=version.id,
                    executed_by=None,
                    status_id=None,
                    attachment_id=None,
                    resolution_id=None,
                    actual_result=None,
                    executed_at=None,
                    execution_order=execution_order,
                )
                self.add(execution)
                created.append(execution)
                execution_order += 1

        self.commit()
        return created

    def update_execution(self, execution_id: int, execution_data: dict[str, Any], current_user: Any):
        execution = self.db.query(Executions).filter(Executions.id == execution_id).first()
        if not execution:
            return None

        test_case_version = TestCaseVersionService(self.db).get_test_case_version_with_test_case(
            execution.test_case_version_id
        )

        update_payload = dict(execution_data)
        update_payload.pop("executed_by", None)
        update_payload.pop("executed_at", None)
        update_payload.pop("updated_by", None)
        update_payload.pop("updated_at", None)

        if update_payload:
            update_payload["updated_by"] = getattr(current_user, "id", current_user)
            update_payload["updated_at"] = datetime.now(timezone.utc)

        if "status_id" in update_payload and update_payload["status_id"] is not None:
            allowed_status_ids = {
                status.id
                for status in self.db.query(Statuses).filter(
                    Statuses.status_set_id == test_case_version.test_case.status_set_id
                ).all()
            }
            if update_payload["status_id"] not in allowed_status_ids:
                raise ValueError("Status is not allowed for this execution")

            update_payload["executed_by"] = getattr(current_user, "id", current_user)
            update_payload["executed_at"] = datetime.now(timezone.utc)

        if "attachment_id" in update_payload and update_payload["attachment_id"] is not None:
            attachment = self.db.query(Attachments).filter(Attachments.id == update_payload["attachment_id"]).first()
            if not attachment:
                raise ValueError("Attachment not found")

        if "resolution_id" in update_payload and update_payload["resolution_id"] is not None:
            resolution = self.db.query(Resolutions).filter(Resolutions.id == update_payload["resolution_id"]).first()
            if not resolution:
                raise ValueError("Resolution not found")

        updated_execution = self.update(execution, update_payload)
        if updated_execution and updated_execution.status_id is not None:
            run = self.db.query(Runs).filter(Runs.id == updated_execution.run_id).first()
            if run and run.done_at is None:
                related_executions = self.db.query(Executions).filter(Executions.run_id == run.id).all()
                if all(item.status_id is not None for item in related_executions):
                    run.done_at = datetime.now(timezone.utc)
                    self.commit()

        return updated_execution

    def delete_execution(self, execution_id: int):
        execution = self.get_execution(execution_id)
        if not execution:
            return None
        return self.delete(execution)

    def assign_execution(self, execution_id: int, user_id: int):
        execution = self.get_execution(execution_id)
        if not execution:
            return None
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return None
        execution.assigned_to = user_id
        self.commit()
        return execution

    def assign_executions_bulk(self, execution_ids: list[int], user_id: int):
        user = self.db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return None
        executions = self.db.query(Executions).filter(Executions.id.in_(execution_ids)).all()
        if len(executions) != len(execution_ids):
            return None
        for execution in executions:
            execution.assigned_to = user_id
        self.commit()
        return executions

    def start_execution(self, execution_id: int, current_user: Any):
        execution = self.get_execution(execution_id)
        if not execution:
            return None
        if execution.assigned_to != current_user.id:
            raise ValueError('Only the assigned user can start this execution')
        if execution.started_at is not None:
            raise ValueError('Execution has already been started')
        execution.started_at = datetime.now(timezone.utc)
        self.commit()
        return execution
