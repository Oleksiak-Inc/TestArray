"""Service-layer tests extracted from the monolithic suite."""

from uuid import uuid4

import pytest

from helpers import _uid


# ===========================================================================
# SERVICE TESTS
# ===========================================================================

def test_base_service_create_and_update_helpers_work(db_session):
    from db.models.clients import Clients
    from app.services.utils.service import BaseService

    class DummyService(BaseService):
        pass

    service = DummyService(db_session)

    client = service.create(Clients, {"name": "BaseClient"})
    assert client.id is not None
    assert client.name == "BaseClient"

    updated = service.update(client, {"name": "UpdatedClient"})
    assert updated.name == "UpdatedClient"

    deleted = service.delete(client)
    assert deleted.id == client.id

class TestAuthService:
    def test_register_creates_user(self, db_session):
        from app.services.auth import AuthService

        svc = AuthService(db_session)
        email = f"auth-{_uid()}@example.com"
        user = svc.register_user("Alice", "Smith", email, "password123")
        assert user is not None
        assert user.email == email

    def test_register_duplicate_email_returns_none(self, db_session):
        from app.services.auth import AuthService

        svc = AuthService(db_session)
        email = f"dup-{_uid()}@example.com"
        svc.register_user("A", "B", email, "password123")
        result = svc.register_user("A", "B", email, "password123")
        assert result is None

    def test_login_returns_token(self, db_session):
        from app.services.auth import AuthService

        svc = AuthService(db_session)
        email = f"login-{_uid()}@example.com"
        svc.register_user("Bob", "Jones", email, "password123")
        result = svc.login_user(email, "password123")
        assert result is not None
        assert "access_token" in result
        assert result["user"].email == email

    def test_login_wrong_password_returns_none(self, db_session):
        from app.services.auth import AuthService

        svc = AuthService(db_session)
        email = f"badpw-{_uid()}@example.com"
        svc.register_user("C", "D", email, "password123")
        result = svc.login_user(email, "wrong")
        assert result is None

    def test_login_unknown_email_returns_none(self, db_session):
        from app.services.auth import AuthService

        svc = AuthService(db_session)
        result = svc.login_user("nobody@example.com", "anything")
        assert result is None

    def test_validate_session_true_and_false(self, db_session):
        from app.services.auth import AuthService

        svc = AuthService(db_session)
        email = f"val-{_uid()}@example.com"
        svc.register_user("E", "F", email, "password123")
        result = svc.login_user(email, "password123")
        token = result["access_token"]

        assert svc.validate_session(token) is True
        assert svc.validate_session("totally-invalid-token") is False

    def test_logout_invalidates_session(self, db_session):
        from app.services.auth import AuthService

        svc = AuthService(db_session)
        email = f"logout-{_uid()}@example.com"
        svc.register_user("G", "H", email, "password123")
        result = svc.login_user(email, "password123")
        token = result["access_token"]

        svc.logout_user(token)
        assert svc.validate_session(token) is False

    def test_logout_unknown_token_returns_none(self, db_session):
        from app.services.auth import AuthService

        svc = AuthService(db_session)
        assert svc.logout_user("no-such-token") is None


class TestSessionService:
    def _register_and_login(self, db_session):
        from app.services.auth import AuthService

        svc = AuthService(db_session)
        email = f"sess-{_uid()}@example.com"
        svc.register_user("X", "Y", email, "password123")
        result = svc.login_user(email, "password123")
        return result["access_token"], result["user"]

    def test_get_session_returns_session(self, db_session):
        from app.services.session import SessionService

        token, _ = self._register_and_login(db_session)
        session = SessionService(db_session).get_session(token)
        assert session is not None

    def test_get_session_missing_returns_none(self, db_session):
        from app.services.session import SessionService

        result = SessionService(db_session).get_session("ghost-token")
        assert result is None

    def test_delete_session_soft_revokes_it(self, db_session):
        from app.services.session import SessionService
        from db.models.revocations import Revocations

        token, _ = self._register_and_login(db_session)
        svc = SessionService(db_session)
        revoked = svc.delete_session(token)

        assert revoked is not None
        session = svc.get_session(token)
        assert session is not None
        assert session.ended_at is not None
        assert session.ended_at <= session.expires_at
        assert db_session.query(Revocations).filter(Revocations.target_session_id == session.id).count() == 1

    def test_delete_missing_session_returns_none(self, db_session):
        from app.services.session import SessionService

        assert SessionService(db_session).delete_session("no-token") is None


class TestUserService:
    def test_get_by_email(self, db_session):
        from app.services.auth import AuthService
        from app.services.users import UserService

        email = f"usvc-{_uid()}@example.com"
        AuthService(db_session).register_user("A", "B", email, "password123")
        user = UserService(db_session).get_user_by_email(email)
        assert user is not None and user.email == email

    def test_get_by_email_missing(self, db_session):
        from app.services.users import UserService

        assert UserService(db_session).get_user_by_email("ghost@example.com") is None

    def test_get_by_id(self, db_session):
        from app.services.auth import AuthService
        from app.services.users import UserService

        email = f"uid-{_uid()}@example.com"
        user = AuthService(db_session).register_user("C", "D", email, "password123")
        found = UserService(db_session).get_user_by_id(user.id)
        assert found is not None and found.id == user.id




class TestClientService:
    def test_create_and_get(self, db_session):
        from app.services.client import ClientService

        svc = ClientService(db_session)
        name = f"Cli-{_uid()}"
        c = svc.create_client({"name": name})
        assert svc.get_client(c.id).name == name

    def test_get_missing(self, db_session):
        from app.services.client import ClientService

        assert ClientService(db_session).get_client(99999) is None

    def test_update(self, db_session, make_client):
        from app.services.client import ClientService

        c = make_client()
        updated = ClientService(db_session).update_client(c.id, {"name": "NewName"})
        assert updated.name == "NewName"

    def test_get_with_projects(self, db_session, make_client, make_project):
        from app.services.client import ClientService

        c = make_client()
        make_project(client=c)
        result = ClientService(db_session).get_client_with_projects(c.id)
        assert len(result.projects) >= 1


class TestProjectService:
    def test_create_and_get(self, db_session, make_client):
        from app.services.project import ProjectService

        c = make_client()
        svc = ProjectService(db_session)
        p = svc.create_project({"name": f"Proj-{_uid()}", "client_id": c.id})
        assert svc.get_project(p.id).client_id == c.id

    def test_get_missing(self, db_session):
        from app.services.project import ProjectService

        assert ProjectService(db_session).get_project(99999) is None

    def test_update(self, db_session, make_project):
        from app.services.project import ProjectService

        p = make_project()
        updated = ProjectService(db_session).update_project(p.id, {"name": "Renamed"})
        assert updated.name == "Renamed"

    def test_get_with_client(self, db_session, make_project, make_client):
        from app.services.project import ProjectService

        c = make_client()
        p = make_project(client=c)
        result = ProjectService(db_session).get_project_with_client(p.id)
        assert result.client.id == c.id


class TestScenarioService:
    def test_full_lifecycle(self, db_session):
        from app.services.scenario import ScenarioService

        svc = ScenarioService(db_session)
        name = f"Scen-{_uid()}"
        sc = svc.create_scenario({"name": name})
        assert svc.get_scenario(sc.id).name == name
        assert svc.get_scenario_by_name(name) is not None
        assert any(s.id == sc.id for s in svc.list_scenarios())
        svc.update_scenario(sc.id, {"name": "Updated"})
        assert svc.get_scenario(sc.id).name == "Updated"
        svc.delete_scenario(sc.id)
        assert svc.get_scenario(sc.id) is None

    def test_delete_missing_returns_none(self, db_session):
        from app.services.scenario import ScenarioService

        assert ScenarioService(db_session).delete_scenario(99999) is None


class TestStatusSetService:
    def test_full_lifecycle(self, db_session):
        from app.services.status_set import StatusSetService

        svc = StatusSetService(db_session)
        name = f"SS-{_uid()}"
        ss = svc.create_status_set({"name": name})
        assert svc.get_status_set(ss.id).name == name
        assert svc.get_status_set_by_name(name) is not None
        assert any(s.id == ss.id for s in svc.list_status_sets())
        svc.update_status_set(ss.id, {"name": "Updated"})
        assert svc.get_status_set(ss.id).name == "Updated"
        svc.delete_status_set(ss.id)
        assert svc.get_status_set(ss.id) is None

    def test_delete_missing_returns_none(self, db_session):
        from app.services.status_set import StatusSetService

        assert StatusSetService(db_session).delete_status_set(99999) is None


class TestDeviceService:
    def _device_data(self, project_id: int) -> dict:
        return {
            "name_external": f"Dev-{_uid()}",
            "name_internal": f"dev-{_uid()}",
            "cpu": "i9",
            "gpu": "RTX 4090",
            "ram": "64GB",
            "project_id": project_id,
        }

    def test_create_and_get(self, db_session, make_project):
        from app.services.device import DeviceService

        p = make_project()
        svc = DeviceService(db_session)
        d = svc.create_device(self._device_data(p.id))
        assert svc.get_device(d.id).project_id == p.id

    def test_get_missing(self, db_session):
        from app.services.device import DeviceService

        assert DeviceService(db_session).get_device(99999) is None

    def test_list_by_project(self, db_session, make_project):
        from app.services.device import DeviceService

        p = make_project()
        svc = DeviceService(db_session)
        svc.create_device(self._device_data(p.id))
        svc.create_device(self._device_data(p.id))
        devices = svc.list_devices_by_project(p.id)
        assert len(devices) >= 2

    def test_update(self, db_session, make_project):
        from app.services.device import DeviceService

        p = make_project()
        svc = DeviceService(db_session)
        d = svc.create_device(self._device_data(p.id))
        updated = svc.update_device(d.id, {"name_external": "Renamed"})
        assert updated.name_external == "Renamed"

    def test_delete(self, db_session, make_project):
        from app.services.device import DeviceService

        p = make_project()
        svc = DeviceService(db_session)
        d = svc.create_device(self._device_data(p.id))
        svc.delete_device(d.id)
        assert svc.get_device(d.id) is None

    def test_delete_missing_returns_none(self, db_session):
        from app.services.device import DeviceService

        assert DeviceService(db_session).delete_device(99999) is None

    def test_get_with_project(self, db_session, make_project):
        from app.services.device import DeviceService

        p = make_project()
        svc = DeviceService(db_session)
        d = svc.create_device(self._device_data(p.id))
        result = svc.get_device_with_project(d.id)
        assert result.project.id == p.id


class TestRunService:
    def test_create_and_get(self, db_session, make_project):
        from app.services.run import RunService

        p = make_project()
        svc = RunService(db_session)
        r = svc.create_run({"name": f"Run-{_uid()}", "project_id": p.id})
        assert svc.get_run(r.id).project_id == p.id

    def test_get_missing(self, db_session):
        from app.services.run import RunService

        assert RunService(db_session).get_run(99999) is None

    def test_list_by_project(self, db_session, make_project):
        from app.services.run import RunService

        p = make_project()
        svc = RunService(db_session)
        svc.create_run({"name": f"R1-{_uid()}", "project_id": p.id})
        svc.create_run({"name": f"R2-{_uid()}", "project_id": p.id})
        runs = svc.list_runs_by_project(p.id)
        assert len(runs) >= 2

    def test_update(self, db_session, make_project):
        from app.services.run import RunService

        p = make_project()
        svc = RunService(db_session)
        r = svc.create_run({"name": f"Run-{_uid()}", "project_id": p.id})
        updated = svc.update_run(r.id, {"name": "Renamed Run"})
        assert updated.name == "Renamed Run"

    def test_delete(self, db_session, make_project):
        from app.services.run import RunService

        p = make_project()
        svc = RunService(db_session)
        r = svc.create_run({"name": f"Run-{_uid()}", "project_id": p.id})
        svc.delete_run(r.id)
        assert svc.get_run(r.id) is None

    def test_delete_missing_returns_none(self, db_session):
        from app.services.run import RunService

        assert RunService(db_session).delete_run(99999) is None

    def test_get_with_project(self, db_session, make_project):
        from app.services.run import RunService

        p = make_project()
        svc = RunService(db_session)
        r = svc.create_run({"name": f"R-{_uid()}", "project_id": p.id})
        result = svc.get_run_with_project(r.id)
        assert result.project.id == p.id

    def test_get_with_project_and_client(self, db_session, make_project, make_client):
        from app.services.run import RunService

        c = make_client()
        p = make_project(client=c)
        svc = RunService(db_session)
        r = svc.create_run({"name": f"R-{_uid()}", "project_id": p.id})
        result = svc.get_run_with_project_and_client(r.id)
        assert result.project.client.id == c.id


class TestTestSuiteService:
    def test_full_lifecycle(self, db_session):
        from app.services.test_suite import TestSuiteService

        svc = TestSuiteService(db_session)
        name = f"Suite-{_uid()}"
        ts = svc.create_test_suite({"name": name})
        assert svc.get_test_suite(ts.id).name == name
        assert svc.get_test_suite_by_name(name) is not None
        assert any(s.id == ts.id for s in svc.list_test_suites())
        svc.update_test_suite(ts.id, {"name": "Updated"})
        assert svc.get_test_suite(ts.id).name == "Updated"
        svc.delete_test_suite(ts.id)
        assert svc.get_test_suite(ts.id) is None

    def test_get_missing(self, db_session):
        from app.services.test_suite import TestSuiteService

        assert TestSuiteService(db_session).get_test_suite(99999) is None

    def test_delete_missing_returns_none(self, db_session):
        from app.services.test_suite import TestSuiteService

        assert TestSuiteService(db_session).delete_test_suite(99999) is None

    def test_get_with_test_cases(self, db_session, make_test_case, make_test_suite):
        from app.services.suitcase import SuitcaseService
        from app.services.test_suite import TestSuiteService

        tc = make_test_case()
        ts = make_test_suite()
        SuitcaseService(db_session).create_suitcase(
            {"test_case_id": tc.id, "test_suite_id": ts.id}
        )
        result = TestSuiteService(db_session).get_test_suite_with_test_cases(ts.id)
        assert len(result.suitcases) >= 1


class TestTestCaseService:
    def test_create_and_get(self, db_session, make_scenario, make_status_set):
        from app.services.test_case import TestCaseService

        s = make_scenario()
        ss = make_status_set()
        svc = TestCaseService(db_session)
        tc = svc.create_test_case({"scenario_id": s.id, "status_set_id": ss.id})
        assert svc.get_test_case(tc.id).id == tc.id

    def test_get_missing(self, db_session):
        from app.services.test_case import TestCaseService

        assert TestCaseService(db_session).get_test_case(99999) is None

    def test_list(self, db_session, make_test_case):
        from app.services.test_case import TestCaseService

        tc = make_test_case()
        all_cases = TestCaseService(db_session).list_test_cases()
        assert any(c.id == tc.id for c in all_cases)

    def test_update(self, db_session, make_test_case, make_scenario):
        from app.services.test_case import TestCaseService

        tc = make_test_case()
        new_sc = make_scenario()
        updated = TestCaseService(db_session).update_test_case(
            tc.id, {"scenario_id": new_sc.id}
        )
        assert updated.scenario_id == new_sc.id

    def test_delete(self, db_session, make_test_case):
        from app.services.test_case import TestCaseService

        tc = make_test_case()
        TestCaseService(db_session).delete_test_case(tc.id)
        assert TestCaseService(db_session).get_test_case(tc.id) is None

    def test_delete_missing_returns_none(self, db_session):
        from app.services.test_case import TestCaseService

        assert TestCaseService(db_session).delete_test_case(99999) is None

    def test_get_with_testsuites(self, db_session, make_test_case, make_test_suite):
        from app.services.suitcase import SuitcaseService
        from app.services.test_case import TestCaseService

        tc = make_test_case()
        ts = make_test_suite()
        SuitcaseService(db_session).create_suitcase(
            {"test_case_id": tc.id, "test_suite_id": ts.id}
        )
        result = TestCaseService(db_session).get_test_case_with_testsuites(tc.id)
        assert len(result.suitcases) >= 1

    def test_create_and_version(self, db_session, make_scenario, make_status_set, current_user):
        from app.services.test_case import TestCaseService

        s = make_scenario()
        ss = make_status_set()
        tc_data = {"scenario_id": s.id, "status_set_id": ss.id}
        tcv_data = {
            "name": "v1",
            "version": 1,
            "description": "desc",
            "steps": "step 1",
            "expected_result": "ok",
            "release_ready": False,
            "created_by": current_user.id,
        }
        tc, tcv = TestCaseService(db_session).create_test_case_and_version(
            tc_data, tcv_data
        )
        assert tc.id is not None
        assert tcv.test_case_id == tc.id

    def test_bulk_create(self, db_session, make_scenario, make_status_set, current_user):
        from app.services.test_case import TestCaseService

        s = make_scenario()
        ss = make_status_set()
        items = [
            {
                "scenario_id": s.id,
                "status_set_id": ss.id,
                "name": f"TC-{_uid()}",
                "description": "d",
                "steps": "s",
                "expected_result": "r",
                "release_ready": False,
            }
            for _ in range(3)
        ]
        results = TestCaseService(db_session).create_test_cases_and_versions_bulk(
            items=items, created_by=current_user.id
        )
        assert len(results) == 3
        for r in results:
            assert "test_case_id" in r
            assert r["version"] == 1

    def test_bulk_create_with_suite(
        self, db_session, make_scenario, make_status_set, make_test_suite, current_user
    ):
        from app.services.test_case import TestCaseService
        from app.services.suitcase import SuitcaseService

        s = make_scenario()
        ss = make_status_set()
        ts = make_test_suite()
        items = [
            {
                "scenario_id": s.id,
                "status_set_id": ss.id,
                "name": f"BTC-{_uid()}",
                "description": "",
                "steps": "",
                "expected_result": "",
                "release_ready": False,
            }
        ]
        results = TestCaseService(db_session).create_test_cases_and_versions_bulk(
            items=items, created_by=current_user.id, test_suite_id=ts.id
        )
        tc_id = results[0]["test_case_id"]
        suitcases = SuitcaseService(db_session).get_suitcases_by_test_case_id(tc_id)
        assert any(sc.test_suite_id == ts.id for sc in suitcases)


class TestPermissionService:
    def test_create_and_get_permission(self, db_session):
        from app.services.permission import PermissionService

        svc = PermissionService(db_session)
        perm = svc.create_permission({"code": f"perm_{_uid()}", "description": "Perm", "scope": "global"})
        assert perm.id is not None
        assert svc.get_permission(perm.id).code == perm.code
        assert svc.get_permission_by_code(perm.code).id == perm.id

    def test_list_permissions(self, db_session):
        from app.services.permission import PermissionService

        svc = PermissionService(db_session)
        svc.create_permission({"code": f"perm_list_{_uid()}", "description": "Perm", "scope": "global"})
        perms = svc.list_permissions()
        assert any(p.code.startswith("perm_list_") for p in perms)

    def test_delete_permission(self, db_session):
        from app.services.permission import PermissionService

        svc = PermissionService(db_session)
        perm = svc.create_permission({"code": f"perm_del_{_uid()}", "description": "Perm", "scope": "global"})
        deleted = svc.delete_permission(perm.id)
        assert deleted.id == perm.id
        assert svc.get_permission(perm.id) is None


class TestRelationTypeService:
    def test_create_and_get_relation_type(self, db_session):
        from app.services.relation_type import RelationTypeService

        svc = RelationTypeService(db_session)
        rt = svc.create_relation_type({"name": f"type-{_uid()}"})
        assert rt.id is not None
        assert svc.get_relation_type(rt.id).name == rt.name
        assert svc.get_relation_type_by_name(rt.name).id == rt.id

    def test_list_relation_types(self, db_session):
        from app.services.relation_type import RelationTypeService

        svc = RelationTypeService(db_session)
        svc.create_relation_type({"name": f"type-list-{_uid()}"})
        types = svc.list_relation_types()
        assert any(t.name.startswith("type-list-") for t in types)

    def test_update_and_delete_relation_type(self, db_session):
        from app.services.relation_type import RelationTypeService

        svc = RelationTypeService(db_session)
        rt = svc.create_relation_type({"name": f"type-upd-{_uid()}"})
        updated = svc.update_relation_type(rt.id, {"name": "UpdatedType"})
        assert updated.name == "UpdatedType"
        deleted = svc.delete_relation_type(rt.id)
        assert deleted.id == rt.id
        assert svc.get_relation_type(rt.id) is None


class TestResolutionService:
    def test_create_and_get_resolution(self, db_session):
        from app.services.resolution import ResolutionService

        svc = ResolutionService(db_session)
        res = svc.create_resolution({"h": 1080, "w": 1920})
        assert res.id is not None
        assert svc.get_resolution(res.id).h == 1080
        assert svc.get_resolution_by_hw(1080, 1920).id == res.id

    def test_list_resolutions(self, db_session):
        from app.services.resolution import ResolutionService

        svc = ResolutionService(db_session)
        svc.create_resolution({"h": 720, "w": 1280})
        results = svc.list_resolutions()
        assert any(r.h == 720 and r.w == 1280 for r in results)

    def test_update_and_delete_resolution(self, db_session):
        from app.services.resolution import ResolutionService

        svc = ResolutionService(db_session)
        res = svc.create_resolution({"h": 600, "w": 800})
        updated = svc.update_resolution(res.id, {"h": 601})
        assert updated.h == 601
        deleted = svc.delete_resolution(res.id)
        assert deleted.id == res.id
        assert svc.get_resolution(res.id) is None


class TestStatusService:
    def test_create_and_get_status(self, db_session, make_status_set):
        from app.services.status import StatusService

        ss = make_status_set()
        svc = StatusService(db_session)
        status = svc.create_status({"name": "OK", "status_set_id": ss.id, "description": "Good"})
        assert status.id is not None
        assert svc.get_status(status.id).name == "OK"
        statuses = svc.list_statuses_by_status_set(ss.id)
        assert any(s.id == status.id for s in statuses)

    def test_list_all_statuses(self, db_session, make_status_set):
        from app.services.status import StatusService

        ss = make_status_set()
        svc = StatusService(db_session)
        svc.create_status({"name": "X", "status_set_id": ss.id, "description": "Desc"})
        all_statuses = svc.list_all_statuses()
        assert len(all_statuses) >= 1

    def test_update_and_delete_status(self, db_session, make_status_set):
        from app.services.status import StatusService

        ss = make_status_set()
        svc = StatusService(db_session)
        status = svc.create_status({"name": "Before", "status_set_id": ss.id, "description": "Desc"})
        updated = svc.update_status(status.id, {"name": "After"})
        assert updated.name == "After"
        deleted = svc.delete_status(status.id)
        assert deleted.id == status.id
        assert svc.get_status(status.id) is None


class TestUserTypeService:
    def test_create_and_get_user_type(self, db_session):
        from app.services.user_type import UserTypeService

        svc = UserTypeService(db_session)
        ut = svc.create_user_type({"name": f"UserType-{_uid()}"})
        assert ut.id is not None
        assert svc.get_user_type_by_id(ut.id).name == ut.name
        assert svc.get_user_type_by_name(ut.name).id == ut.id

    def test_list_user_types(self, db_session):
        from app.services.user_type import UserTypeService

        svc = UserTypeService(db_session)
        svc.create_user_type({"name": f"UserTypeList-{_uid()}"})
        types = svc.list_user_types()
        assert any(t.name.startswith("UserTypeList-") for t in types)

    def test_update_and_delete_user_type(self, db_session):
        from app.services.user_type import UserTypeService

        svc = UserTypeService(db_session)
        ut = svc.create_user_type({"name": f"UserTypeUpd-{_uid()}"})
        updated = svc.update_user_type(ut.id, {"name": "UpdatedType"})
        assert updated.name == "UpdatedType"
        deleted = svc.delete_user_type(ut.id)
        assert deleted.id == ut.id
        assert svc.get_user_type_by_id(ut.id) is None


class TestUserGroupService:
    def test_create_and_get_user_group(self, db_session):
        from app.services.user_group import UserGroupService
        from app.services.auth import AuthService

        auth = AuthService(db_session)
        owner = auth.register_user("Owner", "User", f"owner-{_uid()}@example.com", "password123")
        svc = UserGroupService(db_session)
        group = svc.create_user_group({"name": f"Group-{_uid()}", "owner_id": owner.id, "created_by_id": owner.id})
        assert group.id is not None
        assert svc.get_user_group(group.id).name == group.name
        assert svc.get_user_group_by_name(group.name).id == group.id

    def test_list_user_groups(self, db_session):
        from app.services.user_group import UserGroupService
        from app.services.auth import AuthService

        auth = AuthService(db_session)
        owner = auth.register_user("Owner2", "User", f"owner2-{_uid()}@example.com", "password123")
        svc = UserGroupService(db_session)
        svc.create_user_group({"name": f"GroupList-{_uid()}", "owner_id": owner.id, "created_by_id": owner.id})
        groups = svc.list_user_groups()
        assert any(g.name.startswith("GroupList-") for g in groups)

    def test_update_and_delete_user_group(self, db_session):
        from app.services.user_group import UserGroupService
        from app.services.auth import AuthService

        auth = AuthService(db_session)
        owner = auth.register_user("Owner3", "User", f"owner3-{_uid()}@example.com", "password123")
        svc = UserGroupService(db_session)
        group = svc.create_user_group({"name": f"GroupUpd-{_uid()}", "owner_id": owner.id, "created_by_id": owner.id})
        updated = svc.update_user_group(group.id, {"name": "UpdatedGroup"})
        assert updated.name == "UpdatedGroup"
        deleted = svc.delete_user_group(group.id)
        assert deleted.id == group.id
        assert svc.get_user_group(group.id) is None


class TestGroupMembershipService:
    def test_add_list_and_remove_member(self, db_session):
        from app.services.group_membership import GroupMembershipService
        from app.services.user_group import UserGroupService
        from app.services.auth import AuthService

        auth = AuthService(db_session)
        owner = auth.register_user("Owner4", "User", f"owner4-{_uid()}@example.com", "password123")
        member = auth.register_user("Member", "User", f"member-{_uid()}@example.com", "password123")
        group = UserGroupService(db_session).create_user_group({"name": f"GroupMember-{_uid()}", "owner_id": owner.id, "created_by_id": owner.id})

        svc = GroupMembershipService(db_session)
        membership = svc.add_member(group.id, member.id)
        assert membership.user_id == member.id
        assert membership.group_id == group.id

        members = svc.list_group_members(group.id)
        assert any(m.id == member.id for m in members)

        groups = svc.list_user_groups(member.id)
        assert any(g.id == group.id for g in groups)

        assert svc.remove_member(group.id, member.id) is True
        assert svc.remove_member(group.id, member.id) is False


class TestGroupPermissionService:
    def test_assign_and_list_permissions(self, db_session):
        from app.services.group_permission import GroupPermissionService
        from app.services.user_group import UserGroupService
        from app.services.permission import PermissionService
        from app.services.auth import AuthService

        auth = AuthService(db_session)
        owner = auth.register_user("Owner5", "User", f"owner5-{_uid()}@example.com", "password123")
        group = UserGroupService(db_session).create_user_group({"name": f"GroupPerm-{_uid()}", "owner_id": owner.id, "created_by_id": owner.id})
        perm1 = PermissionService(db_session).create_permission({"code": f"perm1-{_uid()}", "description": "P", "scope": "global"})
        perm2 = PermissionService(db_session).create_permission({"code": f"perm2-{_uid()}", "description": "P", "scope": "global"})

        svc = GroupPermissionService(db_session)
        assignment = svc.assign_permission(group.id, perm1.id)
        assert assignment.group_id == group.id
        assert assignment.permission_id == perm1.id

        assignments = svc.assign_multiple_permissions(group.id, [perm2.id])
        assert assignments[0].permission_id == perm2.id

        perms = svc.list_permissions_for_group(group.id)
        assert any(p.id == perm1.id for p in perms)

        groups = svc.list_groups_for_permission(perm1.id)
        assert any(g.id == group.id for g in groups)

        assert svc.remove_permission(group.id, perm1.id) is True
        assert svc.remove_permission(group.id, perm1.id) is False


class TestSuitcaseService:
    def test_create_and_get_suitcase(self, db_session, make_test_case, make_test_suite):
        from app.services.suitcase import SuitcaseService

        tc = make_test_case()
        ts = make_test_suite()
        svc = SuitcaseService(db_session)
        suitcase = svc.create_suitcase({"test_case_id": tc.id, "test_suite_id": ts.id})
        assert suitcase.id is not None
        assert svc.get_suitcase(suitcase.id).id == suitcase.id
        assert any(s.id == suitcase.id for s in svc.get_suitcases_by_test_case_id(tc.id))
        assert any(s.id == suitcase.id for s in svc.get_suitcases_by_test_suite_id(ts.id))
        assert any(s.id == suitcase.id for s in svc.get_suitcases_by_test_case_and_test_suite_id(tc.id, ts.id))

    def test_bulk_create_and_skip_duplicates(self, db_session, make_test_case, make_test_suite):
        from app.services.suitcase import SuitcaseService

        tc = make_test_case()
        ts = make_test_suite()
        svc = SuitcaseService(db_session)
        result = svc.create_suitcases_bulk(test_suite_id=ts.id, test_case_ids=[tc.id, tc.id])
        assert tc.id in [s.test_case_id for s in result["created"]]
        assert tc.id in result["skipped_duplicate_test_case_ids"]

    def test_update_and_delete_suitcase(self, db_session, make_test_case, make_test_suite):
        from app.services.suitcase import SuitcaseService

        tc = make_test_case()
        ts = make_test_suite()
        svc = SuitcaseService(db_session)
        suitcase = svc.create_suitcase({"test_case_id": tc.id, "test_suite_id": ts.id})
        updated = svc.update_suitcase(suitcase.id, {"test_case_id": tc.id})
        assert updated.id == suitcase.id
        deleted = svc.delete_suitcase(suitcase.id)
        assert deleted.id == suitcase.id
        assert svc.get_suitcase(suitcase.id) is None


class TestTestCaseVersionService:
    def test_create_and_get_version(self, db_session, make_test_case, current_user):
        from app.services.test_case_version import TestCaseVersionService

        tc = make_test_case()
        svc = TestCaseVersionService(db_session)
        version = svc.create_test_case_version(
            {
                "test_case_id": tc.id,
                "version": 1,
                "name": "V1",
                "description": "desc",
                "steps": "steps",
                "expected_result": "result",
                "release_ready": True,
                "created_by": current_user.id,
            }
        )
        assert version.id is not None
        assert svc.get_test_case_version(version.id).id == version.id
        assert svc.get_test_case_version_with_test_case(version.id).test_case.id == tc.id

    def test_latest_release_ready_and_list(self, db_session, make_test_case, current_user):
        from app.services.test_case_version import TestCaseVersionService

        tc = make_test_case()
        svc = TestCaseVersionService(db_session)
        svc.create_test_case_version(
            {
                "test_case_id": tc.id,
                "version": 1,
                "name": "V1",
                "description": "desc",
                "steps": "steps",
                "expected_result": "result",
                "release_ready": False,
                "created_by": current_user.id,
            }
        )
        version2 = svc.create_test_case_version(
            {
                "test_case_id": tc.id,
                "version": 2,
                "name": "V2",
                "description": "desc",
                "steps": "steps",
                "expected_result": "result",
                "release_ready": True,
                "created_by": current_user.id,
            }
        )
        latest = svc.get_latest_test_case_version_by_test_case_id(tc.id)
        assert latest.id == version2.id
        latest_ready = svc.get_latest_release_ready_test_case_version_by_test_case_id(tc.id)
        assert latest_ready.id == version2.id
        versions = svc.list_test_case_versions_by_test_case(tc.id)
        assert any(v.id == version2.id for v in versions)

    def test_update_and_delete_version(self, db_session, make_test_case, current_user):
        from app.services.test_case_version import TestCaseVersionService

        tc = make_test_case()
        svc = TestCaseVersionService(db_session)
        version = svc.create_test_case_version(
            {
                "test_case_id": tc.id,
                "version": 1,
                "name": "V1",
                "description": "desc",
                "steps": "steps",
                "expected_result": "result",
                "release_ready": False,
                "created_by": current_user.id,
            }
        )
        updated = svc.update_test_case_version(version.id, {"name": "UpdatedV1"})
        assert updated.name == "UpdatedV1"
        deleted = svc.delete_test_case_version(version.id)
        assert deleted.id == version.id
        assert svc.get_test_case_version(version.id) is None


class TestExecutionRelationshipService:
    def test_create_and_list_relationships(self, db_session, make_test_case, make_project, make_status_set, make_scenario, current_user):
        from app.services.execution_relationship import ExecutionRelationshipService
        from app.services.execution import ExecutionService
        from app.services.relation_type import RelationTypeService
        from app.services.run import RunService
        from app.services.device import DeviceService
        from app.services.test_case_version import TestCaseVersionService
        from app.services.suitcase import SuitcaseService

        project = make_project()
        run = RunService(db_session).create_run({"name": f"RunRel-{_uid()}", "project_id": project.id})
        device = DeviceService(db_session).create_device(
            {
                "name_external": f"DevRel-{_uid()}",
                "name_internal": f"dev-{_uid()}",
                "cpu": "i9",
                "gpu": "RTX",
                "ram": "32GB",
                "project_id": project.id,
            }
        )
        tc = make_test_case()
        svc_tcv = TestCaseVersionService(db_session)
        svc_tcv.create_test_case_version(
            {
                "test_case_id": tc.id,
                "version": 1,
                "name": "V1",
                "description": "desc",
                "steps": "steps",
                "expected_result": "result",
                "release_ready": False,
                "created_by": current_user.id,
            }
        )
        ts = make_test_case = None
        test_suite = make_test_case
        # ensure the suitcase has a test case and suite
        suite = make_test_suite = None
        # avoid repeated helpers in this test
        from app.services.test_suite import TestSuiteService
        ts = TestSuiteService(db_session).create_test_suite({"name": f"SuiteRel-{_uid()}"})
        SuitcaseService(db_session).create_suitcase({"test_case_id": tc.id, "test_suite_id": ts.id})
        executions = ExecutionService(db_session).create_executions_for_test_suite(
            test_suite_id=ts.id,
            run_id=run.id,
            device_ids=[device.id],
        )
        execution_a = executions[0]
        execution_b = ExecutionService(db_session).create_executions_for_test_suite(
            test_suite_id=ts.id,
            run_id=run.id,
            device_ids=[device.id],
        )
        relation_type = RelationTypeService(db_session).create_relation_type({"name": f"relation-{_uid()}"})
        rel_svc = ExecutionRelationshipService(db_session)
        relationship = rel_svc.create_relationship(execution_a.id, execution_a.id, relation_type.id)
        assert relationship.id is not None
        found = rel_svc.get_relationships_for_execution(execution_a.id)
        assert any(r.id == relationship.id for r in found)
        assert rel_svc.delete_relationship(relationship.id) is True
        assert rel_svc.delete_relationship(relationship.id) is False


class TestExecutionService:
    def test_create_list_get_and_delete_execution(self, db_session, make_project, make_test_case, make_status_set, make_scenario, current_user):
        from app.services.execution import ExecutionService
        from app.services.run import RunService
        from app.services.device import DeviceService
        from app.services.test_case_version import TestCaseVersionService
        from app.services.suitcase import SuitcaseService
        from app.services.test_suite import TestSuiteService

        project = make_project()
        run = RunService(db_session).create_run({"name": f"RunExe-{_uid()}", "project_id": project.id})
        device = DeviceService(db_session).create_device(
            {
                "name_external": f"DevExe-{_uid()}",
                "name_internal": f"dev-{_uid()}",
                "cpu": "i7",
                "gpu": "RTX",
                "ram": "16GB",
                "project_id": project.id,
            }
        )
        tc = make_test_case()
        tcv = TestCaseVersionService(db_session).create_test_case_version(
            {
                "test_case_id": tc.id,
                "version": 1,
                "name": "V1",
                "description": "desc",
                "steps": "steps",
                "expected_result": "result",
                "release_ready": False,
                "created_by": current_user.id,
            }
        )
        ts = TestSuiteService(db_session).create_test_suite({"name": f"SuiteExe-{_uid()}"})
        SuitcaseService(db_session).create_suitcase({"test_case_id": tc.id, "test_suite_id": ts.id})

        svc = ExecutionService(db_session)
        executions = svc.create_executions_for_test_suite(test_suite_id=ts.id, run_id=run.id, device_ids=[device.id])
        assert len(executions) == 1
        execution = svc.get_execution(executions[0].id)
        assert execution.id == executions[0].id

        status = db_session.query(__import__("db.models.statuses", fromlist=["Statuses"]).Statuses).filter(__import__("db.models.statuses", fromlist=["Statuses"]).Statuses.status_set_id == tc.status_set_id).first()
        if not status:
            status = __import__("db.models.statuses", fromlist=["Statuses"]).Statuses(name="Started", status_set_id=tc.status_set_id)
            db_session.add(status)
            db_session.commit()
        updated = svc.update_execution(execution.id, {"status_id": status.id}, current_user)
        assert updated.status_id == status.id
        deleted = svc.delete_execution(execution.id)
        assert deleted.id == execution.id
        assert svc.get_execution(execution.id) is None

    def test_assign_and_start_execution(self, db_session, make_project, make_test_case, make_status_set, make_scenario, current_user):
        from app.services.execution import ExecutionService
        from app.services.run import RunService
        from app.services.device import DeviceService
        from app.services.test_case_version import TestCaseVersionService
        from app.services.suitcase import SuitcaseService
        from app.services.test_suite import TestSuiteService

        project = make_project()
        run = RunService(db_session).create_run({"name": f"RunAssign-{_uid()}", "project_id": project.id})
        device = DeviceService(db_session).create_device(
            {
                "name_external": f"DevAssign-{_uid()}",
                "name_internal": f"dev-{_uid()}",
                "cpu": "i7",
                "gpu": "RTX",
                "ram": "16GB",
                "project_id": project.id,
            }
        )
        tc = make_test_case()
        TestCaseVersionService(db_session).create_test_case_version(
            {
                "test_case_id": tc.id,
                "version": 1,
                "name": "V1",
                "description": "desc",
                "steps": "steps",
                "expected_result": "result",
                "release_ready": False,
                "created_by": current_user.id,
            }
        )
        ts = TestSuiteService(db_session).create_test_suite({"name": f"SuiteAssign-{_uid()}"})
        SuitcaseService(db_session).create_suitcase({"test_case_id": tc.id, "test_suite_id": ts.id})

        svc = ExecutionService(db_session)
        executions = svc.create_executions_for_test_suite(test_suite_id=ts.id, run_id=run.id, device_ids=[device.id])
        execution = executions[0]

        assigned = svc.assign_execution(execution.id, current_user.id)
        assert assigned.assigned_to == current_user.id

        bulk = svc.assign_executions_bulk([execution.id], current_user.id)
        assert len(bulk) == 1

        started = svc.start_execution(execution.id, current_user)
        assert started.started_at is not None


class TestAttachmentService:
    def test_get_and_list_attachments(self, db_session):
        from app.services.attachment import AttachmentService
        from app.services.auth import AuthService
        from db.models.attachments import Attachments

        auth = AuthService(db_session)
        user = auth.register_user("Attach", "User", f"attach-{_uid()}@example.com", "password123")
        attachment = Attachments(
            filename="file.txt",
            relative_path="uploads/file.txt",
            uploaded_by=user.id,
        )
        db_session.add(attachment)
        db_session.commit()

        svc = AttachmentService(db_session)
        assert svc.get_attachment(attachment.id).id == attachment.id
        assert any(a.id == attachment.id for a in svc.list_attachments())
