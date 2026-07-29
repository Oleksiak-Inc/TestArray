"""API endpoint tests extracted from the monolithic suite."""

from uuid import uuid4

import pytest

from helpers import _uid


# ===========================================================================
# API ENDPOINT TESTS
# ===========================================================================


class TestAuthAPI:
    def test_register_and_login(self, client):
        email = f"api-{_uid()}@example.com"
        r = client.post(
            "/api/v1/auth/register",
            json={"first_name": "T", "last_name": "U", "email": email, "password": "password123"},
        )
        assert r.status_code == 200
        assert r.json()["email"] == email

        r2 = client.post(
            "/api/v1/auth/login", json={"email": email, "password": "password123"}
        )
        assert r2.status_code == 200
        assert "session" in r2.cookies

    def test_register_duplicate_returns_400(self, client):
        email = f"dup-{_uid()}@example.com"
        payload = {"first_name": "A", "last_name": "B", "email": email, "password": "password123"}
        assert client.post("/api/v1/auth/register", json=payload).status_code == 200
        assert client.post("/api/v1/auth/register", json=payload).status_code == 400

    def test_register_short_password_returns_422(self, client):
        r = client.post(
            "/api/v1/auth/register",
            json={"first_name": "A", "last_name": "B", "email": f"pw-{_uid()}@x.com", "password": "short"},
        )
        assert r.status_code == 422

    def test_login_bad_credentials_returns_401(self, client):
        r = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrong"},
        )
        assert r.status_code == 401

    def test_me_returns_current_user(self, auth_client):
        r = auth_client.get("/api/v1/auth/me")
        assert r.status_code == 200
        assert "email" in r.json()

    def test_me_unauthenticated_returns_401(self, client):
        assert client.get("/api/v1/auth/me").status_code == 401

    def test_logout_clears_cookie(self, auth_client):
        r = auth_client.post("/api/v1/auth/logout")
        assert r.status_code == 200

    def test_logout_without_session_returns_401(self, client):
        assert client.post("/api/v1/auth/logout").status_code == 401


class TestAttachmentAPI:
    def test_attachment_requires_auth(self, client):
        files = {"file": ("test.txt", b"hello world", "text/plain")}
        r = client.post("/api/v1/attachments/upload", files=files)
        assert r.status_code == 401

    def test_upload_attachment(self, admin_client):
        files = {"file": ("test.txt", b"hello world", "text/plain")}
        r = admin_client.post("/api/v1/attachments/upload", files=files)
        assert r.status_code == 201
        data = r.json()
        assert data["filename"] == "test.txt"

    def test_upload_attachment_rejects_unsupported_extension(self, admin_client):
        files = {"file": ("bad.exe", b"binary", "application/octet-stream")}
        r = admin_client.post("/api/v1/attachments/upload", files=files)
        assert r.status_code == 400


class TestClientAPI:
    def test_create_client_requires_auth(self, client):
        r = client.post("/api/v1/clients/", json={"name": "NoAuthClient"})
        assert r.status_code == 401

    def test_create_client(self, admin_client):
        r = admin_client.post("/api/v1/clients/", json={"name": "Acme"})
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Acme"

    def test_get_client(self, admin_client, make_client):
        c = make_client()
        r = admin_client.get(f"/api/v1/clients/{c.id}")
        assert r.status_code == 200
        assert r.json()["id"] == c.id

    def test_get_client_not_found(self, admin_client):
        r = admin_client.get("/api/v1/clients/99999")
        assert r.status_code == 404


class TestDeviceAPI:
    def test_create_device(self, admin_client, make_project):
        p = make_project()
        payload = {"name_external": "Device-1", "project_id": p.id}
        r = admin_client.post("/api/v1/devices/", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["name_external"] == "Device-1"

    def test_delete_device(self, admin_client, make_project):
        p = make_project()
        payload = {"name_external": "Device-Del", "project_id": p.id}
        create = admin_client.post("/api/v1/devices/", json=payload)
        did = create.json()["id"]
        r = admin_client.delete(f"/api/v1/devices/{did}")
        assert r.status_code == 204

    def test_delete_device_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/devices/99999")
        assert r.status_code == 404

    def test_device_requires_auth(self, client, make_project):
        p = make_project()
        payload = {"name_external": "Device-NoAuth", "project_id": p.id}
        r = client.post("/api/v1/devices/", json=payload)
        assert r.status_code == 401

    def test_get_device(self, admin_client, make_project):
        p = make_project()
        payload = {"name_external": "Device-Get", "project_id": p.id}
        create = admin_client.post("/api/v1/devices/", json=payload)
        did = create.json()["id"]
        r = admin_client.get(f"/api/v1/devices/{did}")
        assert r.status_code == 200
        assert r.json()["id"] == did

    def test_get_device_not_found(self, admin_client):
        r = admin_client.get("/api/v1/devices/99999")
        assert r.status_code == 404

    def test_list_devices_by_project(self, admin_client, make_project):
        p = make_project()
        for i in range(2):
            admin_client.post("/api/v1/devices/", json={"name_external": f"D{i}", "project_id": p.id})
        r = admin_client.get(f"/api/v1/devices/project/{p.id}")
        assert r.status_code == 200
        assert len(r.json()) >= 2

    def test_update_device(self, admin_client, make_project):
        p = make_project()
        create = admin_client.post("/api/v1/devices/", json={"name_external": "Old", "project_id": p.id})
        did = create.json()["id"]
        r = admin_client.patch(f"/api/v1/devices/{did}", json={"name_external": "New"})
        assert r.status_code == 200
        assert r.json()["name_external"] == "New"

    def test_update_device_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/devices/99999", json={"name": "x"})
        assert r.status_code == 404


class TestProjectAPI:
    def test_create_project_requires_auth(self, client, make_client):
        c = make_client()
        r = client.post("/api/v1/projects/", json={"name": "P1", "client_id": c.id})
        assert r.status_code == 401

    def test_create_project(self, admin_client, make_client):
        c = make_client()
        r = admin_client.post("/api/v1/projects/", json={"name": "Proj-A", "client_id": c.id})
        assert r.status_code == 201
        assert r.json()["name"] == "Proj-A"

    def test_get_project(self, admin_client, make_project):
        p = make_project()
        r = admin_client.get(f"/api/v1/projects/{p.id}")
        assert r.status_code == 200
        assert r.json()["id"] == p.id

    def test_get_project_not_found(self, admin_client):
        r = admin_client.get("/api/v1/projects/99999")
        assert r.status_code == 404

    def test_get_project_with_client(self, admin_client, make_project):
        p = make_project()
        r = admin_client.get(f"/api/v1/projects/{p.id}/with-client")
        assert r.status_code == 200
        assert r.json()["id"] == p.id

    def test_update_project(self, admin_client, make_project):
        p = make_project()
        r = admin_client.patch(f"/api/v1/projects/{p.id}", json={"name": "NewName"})
        assert r.status_code == 200
        assert r.json()["name"] == "NewName"

    def test_update_project_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/projects/99999", json={"name": "x"})
        assert r.status_code == 404


class TestResolutionAPI:
    def test_create_resolution(self, admin_client):
        r = admin_client.post("/api/v1/resolutions/", json={"w": 1920, "h": 1080})
        assert r.status_code == 201
        assert r.json()["w"] == 1920

    def test_delete_resolution(self, admin_client):
        create = admin_client.post("/api/v1/resolutions/", json={"w": 10, "h": 10})
        rid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/resolutions/{rid}")
        assert r.status_code == 204

    def test_delete_resolution_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/resolutions/99999")
        assert r.status_code == 404

    def test_get_resolution(self, admin_client):
        create = admin_client.post("/api/v1/resolutions/", json={"w": 20, "h": 20})
        rid = create.json()["id"]
        r = admin_client.get(f"/api/v1/resolutions/{rid}")
        assert r.status_code == 200
        assert r.json()["id"] == rid

    def test_get_resolution_not_found(self, admin_client):
        r = admin_client.get("/api/v1/resolutions/99999")
        assert r.status_code == 404

    def test_list_resolutions(self, admin_client):
        admin_client.post("/api/v1/resolutions/", json={"w": 1, "h": 1})
        r = admin_client.get("/api/v1/resolutions/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_resolution_requires_auth(self, client):
        r = client.post("/api/v1/resolutions/", json={"w": 3, "h": 3})
        assert r.status_code == 401

    def test_update_resolution(self, admin_client):
        create = admin_client.post("/api/v1/resolutions/", json={"w": 5, "h": 5})
        rid = create.json()["id"]
        r = admin_client.patch(f"/api/v1/resolutions/{rid}", json={"w": 6})
        assert r.status_code == 200
        assert r.json()["w"] == 6

    def test_update_resolution_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/resolutions/99999", json={"w": 7})
        assert r.status_code == 404


class TestRunAPI:
    def test_create_run_requires_auth(self, client, make_project):
        p = make_project()
        r = client.post("/api/v1/runs/", json={"name": "Run 1", "project_id": p.id})
        assert r.status_code == 401

    def test_create_run(self, admin_client, make_project):
        p = make_project()
        r = admin_client.post("/api/v1/runs/", json={"name": "Run A", "project_id": p.id})
        assert r.status_code == 201
        assert r.json()["name"] == "Run A"

    def test_delete_run(self, admin_client, make_project):
        p = make_project()
        create = admin_client.post("/api/v1/runs/", json={"name": "Run Del", "project_id": p.id})
        rid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/runs/{rid}")
        assert r.status_code == 204

    def test_delete_run_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/runs/99999")
        assert r.status_code == 404

    def test_get_run(self, admin_client, make_project):
        p = make_project()
        create = admin_client.post("/api/v1/runs/", json={"name": "Run Get", "project_id": p.id})
        rid = create.json()["id"]
        r = admin_client.get(f"/api/v1/runs/{rid}")
        assert r.status_code == 200
        assert r.json()["id"] == rid

    def test_get_run_not_found(self, admin_client):
        r = admin_client.get("/api/v1/runs/99999")
        assert r.status_code == 404

    def test_list_runs_by_project(self, admin_client, make_project):
        p = make_project()
        for i in range(2):
            admin_client.post("/api/v1/runs/", json={"name": f"Run{i}", "project_id": p.id})
        r = admin_client.get(f"/api/v1/runs/project/{p.id}")
        assert r.status_code == 200
        assert len(r.json()) >= 2

    def test_update_run(self, admin_client, make_project):
        p = make_project()
        create = admin_client.post("/api/v1/runs/", json={"name": "Old Run", "project_id": p.id})
        rid = create.json()["id"]
        r = admin_client.patch(f"/api/v1/runs/{rid}", json={"name": "New Run"})
        assert r.status_code == 200
        assert r.json()["name"] == "New Run"

    def test_update_run_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/runs/99999", json={"name": "x"})
        assert r.status_code == 404


class TestScenarioAPI:
    def test_create_scenario(self, admin_client):
        r = admin_client.post("/api/v1/scenarios/", json={"name": "Scenario A"})
        assert r.status_code == 201
        assert r.json()["name"] == "Scenario A"

    def test_delete_scenario(self, admin_client):
        create = admin_client.post("/api/v1/scenarios/", json={"name": "Scenario Del"})
        sid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/scenarios/{sid}")
        assert r.status_code == 204

    def test_delete_scenario_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/scenarios/99999")
        assert r.status_code == 404

    def test_get_scenario(self, admin_client):
        create = admin_client.post("/api/v1/scenarios/", json={"name": "Scenario Get"})
        sid = create.json()["id"]
        r = admin_client.get(f"/api/v1/scenarios/{sid}")
        assert r.status_code == 200
        assert r.json()["id"] == sid

    def test_get_scenario_not_found(self, admin_client):
        r = admin_client.get("/api/v1/scenarios/99999")
        assert r.status_code == 404

    def test_list_scenarios(self, admin_client):
        admin_client.post("/api/v1/scenarios/", json={"name": "Scenario One"})
        r = admin_client.get("/api/v1/scenarios/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_scenario_requires_auth(self, client):
        r = client.post("/api/v1/scenarios/", json={"name": "Scenario No Auth"})
        assert r.status_code == 401

    def test_update_scenario(self, admin_client):
        create = admin_client.post("/api/v1/scenarios/", json={"name": "Old"})
        sid = create.json()["id"]
        r = admin_client.patch(f"/api/v1/scenarios/{sid}", json={"name": "New"})
        assert r.status_code == 200
        assert r.json()["name"] == "New"

    def test_update_scenario_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/scenarios/99999", json={"name": "x"})
        assert r.status_code == 404


class TestStatusSetAPI:
    def test_create_status_set(self, admin_client):
        r = admin_client.post("/api/v1/status-sets/", json={"name": "Set A"})
        assert r.status_code == 201
        assert r.json()["name"] == "Set A"

    def test_delete_status_set(self, admin_client):
        create = admin_client.post("/api/v1/status-sets/", json={"name": "DeleteSet"})
        ssid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/status-sets/{ssid}")
        assert r.status_code == 204

    def test_delete_status_set_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/status-sets/99999")
        assert r.status_code == 404

    def test_get_status_set(self, admin_client):
        create = admin_client.post("/api/v1/status-sets/", json={"name": "GetSet"})
        ssid = create.json()["id"]
        r = admin_client.get(f"/api/v1/status-sets/{ssid}")
        assert r.status_code == 200
        assert r.json()["id"] == ssid

    def test_get_status_set_not_found(self, admin_client):
        r = admin_client.get("/api/v1/status-sets/99999")
        assert r.status_code == 404

    def test_list_status_sets(self, admin_client):
        admin_client.post("/api/v1/status-sets/", json={"name": "Set1"})
        r = admin_client.get("/api/v1/status-sets/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_status_set_requires_auth(self, client):
        r = client.post("/api/v1/status-sets/", json={"name": "NoAuth"})
        assert r.status_code == 401

    def test_update_status_set(self, admin_client):
        create = admin_client.post("/api/v1/status-sets/", json={"name": "Old"})
        ssid = create.json()["id"]
        r = admin_client.patch(f"/api/v1/status-sets/{ssid}", json={"name": "New"})
        assert r.status_code == 200
        assert r.json()["name"] == "New"

    def test_update_status_set_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/status-sets/99999", json={"name": "x"})
        assert r.status_code == 404


class TestStatusAPI:
    def test_create_status(self, admin_client, make_status_set):
        ss = make_status_set()
        r = admin_client.post("/api/v1/status/", json={"status_set_id": ss.id, "name": "OK", "description": "ok"})
        assert r.status_code == 201
        assert r.json()["name"] == "OK"

    def test_delete_status(self, admin_client, make_status_set):
        ss = make_status_set()
        create = admin_client.post("/api/v1/status/", json={"status_set_id": ss.id, "name": "Del", "description": "desc"})
        sid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/status/{sid}")
        assert r.status_code == 204

    def test_delete_status_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/status/99999")
        assert r.status_code == 404

    def test_get_status(self, admin_client, make_status_set):
        ss = make_status_set()
        create = admin_client.post("/api/v1/status/", json={"status_set_id": ss.id, "name": "Get", "description": "desc"})
        sid = create.json()["id"]
        r = admin_client.get(f"/api/v1/status/{sid}")
        assert r.status_code == 200
        assert r.json()["id"] == sid

    def test_get_status_not_found(self, admin_client):
        r = admin_client.get("/api/v1/status/99999")
        assert r.status_code == 404

    def test_list_all_statuses(self, admin_client, make_status_set):
        ss = make_status_set()
        admin_client.post("/api/v1/status/", json={"status_set_id": ss.id, "name": "A", "description": "a"})
        r = admin_client.get("/api/v1/status/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_list_statuses_by_set(self, admin_client, make_status_set):
        ss = make_status_set()
        admin_client.post("/api/v1/status/", json={"status_set_id": ss.id, "name": "A", "description": "a"})
        r = admin_client.get(f"/api/v1/status/?status_set_id={ss.id}")
        assert r.status_code == 200
        assert all(item["status_set_id"] == ss.id for item in r.json())

    def test_status_requires_auth(self, client, make_status_set):
        ss = make_status_set()
        r = client.post("/api/v1/status/", json={"status_set_id": ss.id, "name": "NoAuth", "description": "no"})
        assert r.status_code == 401

    def test_update_status(self, admin_client, make_status_set):
        ss = make_status_set()
        create = admin_client.post("/api/v1/status/", json={"status_set_id": ss.id, "name": "Old", "description": "old"})
        sid = create.json()["id"]
        r = admin_client.patch(f"/api/v1/status/{sid}", json={"name": "New"})
        assert r.status_code == 200
        assert r.json()["name"] == "New"

    def test_update_status_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/status/99999", json={"name": "x"})
        assert r.status_code == 404


class TestSuitcaseAPI:
    def test_bulk_create(self, admin_client, make_test_case, make_test_suite):
        tc1 = make_test_case()
        tc2 = make_test_case()
        ts = make_test_suite()
        r = admin_client.post(
            "/api/v1/suitcases/bulk",
            json={"test_suite_id": ts.id, "test_case_ids": [tc1.id, tc2.id]},
        )
        assert r.status_code == 201
        assert len(r.json()["created"]) == 2

    def test_bulk_create_bad_suite_returns_404(self, admin_client, make_test_case):
        tc1 = make_test_case()
        r = admin_client.post(
            "/api/v1/suitcases/bulk",
            json={"test_suite_id": 99999, "test_case_ids": [tc1.id]},
        )
        assert r.status_code == 404

    def test_bulk_create_bad_tc_returns_404(self, admin_client, make_test_suite):
        ts = make_test_suite()
        r = admin_client.post(
            "/api/v1/suitcases/bulk",
            json={"test_suite_id": ts.id, "test_case_ids": [99999]},
        )
        assert r.status_code == 404

    def test_create_suitcase(self, admin_client, make_test_case, make_test_suite):
        tc = make_test_case()
        ts = make_test_suite()
        r = admin_client.post("/api/v1/suitcases/", json={"test_case_id": tc.id, "test_suite_id": ts.id})
        assert r.status_code == 201
        assert r.json()["test_case_id"] == tc.id

    def test_delete_suitcase(self, admin_client, make_test_case, make_test_suite):
        tc = make_test_case()
        ts = make_test_suite()
        create = admin_client.post("/api/v1/suitcases/", json={"test_case_id": tc.id, "test_suite_id": ts.id})
        sid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/suitcases/{sid}")
        assert r.status_code == 204

    def test_delete_suitcase_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/suitcases/99999")
        assert r.status_code == 404

    def test_get_suitcase(self, admin_client, make_test_case, make_test_suite):
        tc = make_test_case()
        ts = make_test_suite()
        create = admin_client.post("/api/v1/suitcases/", json={"test_case_id": tc.id, "test_suite_id": ts.id})
        sid = create.json()["id"]
        r = admin_client.get(f"/api/v1/suitcases/{sid}")
        assert r.status_code == 200
        assert r.json()["id"] == sid

    def test_get_suitcase_not_found(self, admin_client):
        r = admin_client.get("/api/v1/suitcases/99999")
        assert r.status_code == 404

    def test_list_by_test_case(self, admin_client, make_test_case, make_test_suite):
        tc = make_test_case()
        ts = make_test_suite()
        admin_client.post("/api/v1/suitcases/", json={"test_case_id": tc.id, "test_suite_id": ts.id})
        r = admin_client.get(f"/api/v1/suitcases/test-case/{tc.id}")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_list_by_test_suite(self, admin_client, make_test_case, make_test_suite):
        tc = make_test_case()
        ts = make_test_suite()
        admin_client.post("/api/v1/suitcases/", json={"test_case_id": tc.id, "test_suite_id": ts.id})
        r = admin_client.get(f"/api/v1/suitcases/test-suite/{ts.id}")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_suitcase_requires_auth(self, client, make_test_case, make_test_suite):
        tc = make_test_case()
        ts = make_test_suite()
        r = client.post("/api/v1/suitcases/", json={"test_case_id": tc.id, "test_suite_id": ts.id})
        assert r.status_code == 401

    def test_update_suitcase(self, admin_client, make_test_case, make_test_suite):
        tc = make_test_case()
        ts = make_test_suite()
        create = admin_client.post("/api/v1/suitcases/", json={"test_case_id": tc.id, "test_suite_id": ts.id})
        sid = create.json()["id"]
        new_tc = make_test_case()
        r = admin_client.patch(f"/api/v1/suitcases/{sid}", json={"test_case_id": new_tc.id})
        assert r.status_code == 200
        assert r.json()["test_case_id"] == new_tc.id

    def test_update_suitcase_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/suitcases/99999", json={"test_case_id": 1})
        assert r.status_code == 404


class TestTestCaseAPI:
    def test_create_test_case(self, admin_client, make_scenario, make_status_set):
        s = make_scenario()
        ss = make_status_set()
        r = admin_client.post("/api/v1/test-cases/", json={"scenario_id": s.id, "status_set_id": ss.id})
        assert r.status_code == 201
        assert r.json()["scenario_id"] == s.id

    def test_delete_test_case(self, admin_client, make_scenario, make_status_set):
        s = make_scenario()
        ss = make_status_set()
        create = admin_client.post("/api/v1/test-cases/", json={"scenario_id": s.id, "status_set_id": ss.id})
        tid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/test-cases/{tid}")
        assert r.status_code == 204

    def test_delete_test_case_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/test-cases/99999")
        assert r.status_code == 404

    def test_get_test_case(self, admin_client, make_scenario, make_status_set):
        s = make_scenario()
        ss = make_status_set()
        create = admin_client.post("/api/v1/test-cases/", json={"scenario_id": s.id, "status_set_id": ss.id})
        tid = create.json()["id"]
        r = admin_client.get(f"/api/v1/test-cases/{tid}")
        assert r.status_code == 200
        assert r.json()["id"] == tid

    def test_get_test_case_not_found(self, admin_client):
        r = admin_client.get("/api/v1/test-cases/99999")
        assert r.status_code == 404

    def test_list_test_cases(self, admin_client, make_scenario, make_status_set):
        s = make_scenario()
        ss = make_status_set()
        admin_client.post("/api/v1/test-cases/", json={"scenario_id": s.id, "status_set_id": ss.id})
        r = admin_client.get("/api/v1/test-cases/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_test_case_requires_auth(self, client, make_scenario, make_status_set):
        s = make_scenario()
        ss = make_status_set()
        r = client.post("/api/v1/test-cases/", json={"scenario_id": s.id, "status_set_id": ss.id})
        assert r.status_code == 401

    def test_update_test_case(self, admin_client, make_scenario, make_status_set):
        s = make_scenario()
        ss = make_status_set()
        create = admin_client.post("/api/v1/test-cases/", json={"scenario_id": s.id, "status_set_id": ss.id})
        tid = create.json()["id"]
        new_ss = make_status_set()
        r = admin_client.patch(f"/api/v1/test-cases/{tid}", json={"status_set_id": new_ss.id})
        assert r.status_code == 200
        assert r.json()["status_set_id"] == new_ss.id

    def test_update_test_case_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/test-cases/99999", json={"status_set_id": 1})
        assert r.status_code == 404


class TestTestCaseVersionAPI:
    def test_create_version(self, admin_client, make_test_case):
        td = make_test_case()
        r = admin_client.post(
            "/api/v1/test-case-versions/",
            json={"test_case_id": td.id, "version": 1, "name": "V1", "description": "desc", "steps": "steps", "expected_result": "result", "release_ready": False},
        )
        assert r.status_code == 201
        assert r.json()["test_case_id"] == td.id

    def test_delete_version(self, admin_client, make_test_case):
        tc = make_test_case()
        create = admin_client.post(
            "/api/v1/test-case-versions/",
            json={"test_case_id": tc.id, "version": 1, "name": "V1", "description": "desc", "steps": "steps", "expected_result": "result", "release_ready": False},
        )
        vid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/test-case-versions/{vid}")
        assert r.status_code == 204

    def test_delete_version_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/test-case-versions/99999")
        assert r.status_code == 404

    def test_get_version(self, admin_client, make_test_case):
        tc = make_test_case()
        create = admin_client.post(
            "/api/v1/test-case-versions/",
            json={"test_case_id": tc.id, "version": 1, "name": "V1", "description": "desc", "steps": "steps", "expected_result": "result", "release_ready": False},
        )
        vid = create.json()["id"]
        r = admin_client.get(f"/api/v1/test-case-versions/{vid}")
        assert r.status_code == 200
        assert r.json()["id"] == vid

    def test_get_version_not_found(self, admin_client):
        r = admin_client.get("/api/v1/test-case-versions/99999")
        assert r.status_code == 404

    def test_list_versions_by_test_case(self, admin_client, make_test_case):
        tc = make_test_case()
        admin_client.post(
            "/api/v1/test-case-versions/",
            json={"test_case_id": tc.id, "version": 1, "name": "V1", "description": "desc", "steps": "steps", "expected_result": "result", "release_ready": False},
        )
        r = admin_client.get(f"/api/v1/test-case-versions/test-case/{tc.id}")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_version_requires_auth(self, client, make_test_case):
        tc = make_test_case()
        r = client.post(
            "/api/v1/test-case-versions/",
            json={"test_case_id": tc.id, "version": 1, "name": "V1", "description": "desc", "steps": "steps", "expected_result": "result", "release_ready": False},
        )
        assert r.status_code == 401

    def test_update_version(self, admin_client, make_test_case):
        tc = make_test_case()
        create = admin_client.post(
            "/api/v1/test-case-versions/",
            json={"test_case_id": tc.id, "version": 1, "name": "V1", "description": "desc", "steps": "steps", "expected_result": "result", "release_ready": False},
        )
        vid = create.json()["id"]
        r = admin_client.patch(f"/api/v1/test-case-versions/{vid}", json={"release_ready": True})
        assert r.status_code == 200
        assert r.json()["release_ready"] is True

    def test_update_version_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/test-case-versions/99999", json={"release_ready": True})
        assert r.status_code == 404


class TestTestSuiteAPI:
    def test_create_test_suite(self, admin_client):
        r = admin_client.post("/api/v1/test-suites/", json={"name": "Suite A"})
        assert r.status_code == 201
        assert r.json()["name"] == "Suite A"

    def test_delete_test_suite(self, admin_client):
        create = admin_client.post("/api/v1/test-suites/", json={"name": "DelSuite"})
        sid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/test-suites/{sid}")
        assert r.status_code == 204

    def test_delete_test_suite_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/test-suites/99999")
        assert r.status_code == 404

    def test_get_test_suite(self, admin_client):
        create = admin_client.post("/api/v1/test-suites/", json={"name": "GetSuite"})
        sid = create.json()["id"]
        r = admin_client.get(f"/api/v1/test-suites/{sid}")
        assert r.status_code == 200
        assert r.json()["id"] == sid

    def test_get_test_suite_by_name(self, admin_client):
        create = admin_client.post("/api/v1/test-suites/", json={"name": "ByName"})
        r = admin_client.get(f"/api/v1/test-suites/by-name/{create.json()["name"]}")
        assert r.status_code == 200
        assert r.json()["name"] == "ByName"

    def test_get_test_suite_by_name_not_found(self, admin_client):
        r = admin_client.get("/api/v1/test-suites/by-name/does-not-exist")
        assert r.status_code == 404

    def test_list_test_suites(self, admin_client):
        admin_client.post("/api/v1/test-suites/", json={"name": "Suite List"})
        r = admin_client.get("/api/v1/test-suites/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_test_suite_requires_auth(self, client):
        r = client.post("/api/v1/test-suites/", json={"name": "NoAuth"})
        assert r.status_code == 401

    def test_update_test_suite(self, admin_client):
        create = admin_client.post("/api/v1/test-suites/", json={"name": "OldSuite"})
        sid = create.json()["id"]
        r = admin_client.patch(f"/api/v1/test-suites/{sid}", json={"name": "NewSuite"})
        assert r.status_code == 200
        assert r.json()["name"] == "NewSuite"

    def test_update_test_suite_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/test-suites/99999", json={"name": "x"})
        assert r.status_code == 404


class TestUserGroupAPI:
    def test_create_user_group(self, admin_client, db_session):
        from db.models.groups_members import GroupsMembers
        from db.models.user_groups import UserGroups

        group = db_session.query(UserGroups).filter(UserGroups.name == "superadmin").first()
        assert group is not None
        owner_id = db_session.query(GroupsMembers.user_id).filter(GroupsMembers.group_id == group.id).first()[0]
        r = admin_client.post("/api/v1/user-groups/", json={"name": "Team A", "owner_id": owner_id})
        assert r.status_code == 201
        assert r.json()["name"] == "Team A"

    def test_delete_user_group(self, admin_client, db_session):
        from db.models.groups_members import GroupsMembers
        from db.models.user_groups import UserGroups
        group = db_session.query(UserGroups).filter(UserGroups.name == "superadmin").first()
        owner_id = db_session.query(GroupsMembers.user_id).filter(GroupsMembers.group_id == group.id).first()[0]
        create = admin_client.post("/api/v1/user-groups/", json={"name": "DeleteGroup", "owner_id": owner_id})
        gid = create.json()["id"]
        r = admin_client.delete(f"/api/v1/user-groups/{gid}")
        assert r.status_code == 204

    def test_delete_user_group_not_found(self, admin_client):
        r = admin_client.delete("/api/v1/user-groups/99999")
        assert r.status_code == 404

    def test_get_user_group(self, admin_client, db_session):
        from db.models.groups_members import GroupsMembers
        from db.models.user_groups import UserGroups
        group = db_session.query(UserGroups).filter(UserGroups.name == "superadmin").first()
        owner_id = db_session.query(GroupsMembers.user_id).filter(GroupsMembers.group_id == group.id).first()[0]
        create = admin_client.post("/api/v1/user-groups/", json={"name": "GetGroup", "owner_id": owner_id})
        gid = create.json()["id"]
        r = admin_client.get(f"/api/v1/user-groups/{gid}")
        assert r.status_code == 200
        assert r.json()["id"] == gid

    def test_get_user_group_not_found(self, admin_client):
        r = admin_client.get("/api/v1/user-groups/99999")
        assert r.status_code == 404

    def test_list_user_groups(self, admin_client):
        r = admin_client.get("/api/v1/user-groups/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_update_user_group(self, admin_client, db_session):
        from db.models.groups_members import GroupsMembers
        from db.models.user_groups import UserGroups
        group = db_session.query(UserGroups).filter(UserGroups.name == "superadmin").first()
        owner_id = db_session.query(GroupsMembers.user_id).filter(GroupsMembers.group_id == group.id).first()[0]
        create = admin_client.post("/api/v1/user-groups/", json={"name": "UpGroup", "owner_id": owner_id})
        gid = create.json()["id"]
        r = admin_client.patch(f"/api/v1/user-groups/{gid}", json={"name": "Updated"})
        assert r.status_code == 200
        assert r.json()["name"] == "Updated"

    def test_update_user_group_not_found(self, admin_client):
        r = admin_client.patch("/api/v1/user-groups/99999", json={"name": "x"})
        assert r.status_code == 404


class TestUsersAPI:
    def test_get_self(self, auth_client):
        r = auth_client.get("/api/v1/users/me")
        assert r.status_code == 200
        assert "email" in r.json()

    def test_patch_self(self, auth_client):
        r = auth_client.patch("/api/v1/users/me", json={"first_name": "Updated"})
        assert r.status_code == 200
        assert r.json()["first_name"] == "Updated"

    def test_users_self_endpoints_require_auth(self, client):
        r = client.patch("/api/v1/users/me", json={"first_name": "X"})
        assert r.status_code == 401

    def test_get_user_admin(self, admin_client, client):
        email = f"user-{_uid()}@example.com"
        register = client.post(
            "/api/v1/auth/register",
            json={"first_name": "User", "last_name": "Two", "email": email, "password": "password123"},
        )
        uid = register.json()["id"]
        r = admin_client.get(f"/api/v1/users/{uid}")
        assert r.status_code == 200
        assert r.json()["id"] == uid

    def test_get_user_not_found(self, admin_client):
        r = admin_client.get("/api/v1/users/99999")
        assert r.status_code == 404

    def test_list_users_admin(self, admin_client):
        r = admin_client.get("/api/v1/users/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_users_admin_requires_admin(self, auth_client):
        r = auth_client.get("/api/v1/users/")
        assert r.status_code == 403

    def test_admin_update_user(self, admin_client, client):
        email = f"user2-{_uid()}@example.com"
        register = client.post(
            "/api/v1/auth/register",
            json={"first_name": "User", "last_name": "Three", "email": email, "password": "password123"},
        )
        uid = register.json()["id"]
        r = admin_client.patch(f"/api/v1/users/{uid}", json={"active": False})
        assert r.status_code == 200
        assert r.json()["active"] is False

    def test_admin_delete_user(self, admin_client, client):
        email = f"user3-{_uid()}@example.com"
        register = client.post(
            "/api/v1/auth/register",
            json={"first_name": "User", "last_name": "Four", "email": email, "password": "password123"},
        )
        uid = register.json()["id"]
        r = admin_client.delete(f"/api/v1/users/{uid}")
        assert r.status_code == 204