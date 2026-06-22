from uuid import uuid4
import pytest
from app.services.device import DeviceService
from app.services.run import RunService
from app.services.test_suite import TestSuiteService
from app.services.test_case import TestCaseService
from app.services.test_case_version import TestCaseVersionService
from app.services.suitcase import SuitcaseService
from app.services.scenario import ScenarioService
from app.services.status_set import StatusSetService
from db.models.devices import Devices
from db.models.runs import Runs
from db.models.test_suites import TestSuites
from db.models.test_cases import TestCases
from db.models.test_case_versions import TestCaseVersions
from db.models.suitcases import Suitcases


def test_device_crud(auth_client, db_session):
    """Test Device CRUD operations"""
    # Create a project first
    from app.services.client import ClientService
    from app.services.project import ProjectService
    
    client_service = ClientService(db_session)
    client = client_service.create_client({"name": f"Client {uuid4().hex[:8]}"})
    
    project_service = ProjectService(db_session)
    project = project_service.create_project({
        "name": f"Project {uuid4().hex[:8]}", 
        "client_id": client.id
    })
    
    # Create device
    device_payload = {
        "name_external": "Device-1",
        "name_internal": "device1",
        "cpu": "Intel i7",
        "gpu": "NVIDIA RTX 3080",
        "ram": 32,
        "project_id": project.id
    }
    response = auth_client.post("/api/v1/devices/", json=device_payload)
    assert response.status_code == 201
    device_data = response.json()
    assert device_data["name_external"] == device_payload["name_external"]
    device_id = device_data["id"]
    
    # Get device
    response = auth_client.get(f"/api/v1/devices/{device_id}")
    assert response.status_code == 200
    assert response.json()["name_external"] == device_payload["name_external"]
    
    # List devices by project
    response = auth_client.get(f"/api/v1/devices/project/{project.id}")
    assert response.status_code == 200
    devices = response.json()
    assert len(devices) > 0
    assert any(d["id"] == device_id for d in devices)
    
    # Update device
    updated_payload = {"name_external": "Device-Updated"}
    response = auth_client.patch(f"/api/v1/devices/{device_id}", json=updated_payload)
    assert response.status_code == 200
    assert response.json()["name_external"] == "Device-Updated"
    
    # Delete device
    response = auth_client.delete(f"/api/v1/devices/{device_id}")
    assert response.status_code == 204
    
    # Verify deletion
    response = auth_client.get(f"/api/v1/devices/{device_id}")
    assert response.status_code == 404


def test_run_crud(auth_client, db_session):
    """Test Run CRUD operations"""
    from app.services.client import ClientService
    from app.services.project import ProjectService
    from datetime import datetime
    
    client_service = ClientService(db_session)
    client = client_service.create_client({"name": f"Client {uuid4().hex[:8]}"})
    
    project_service = ProjectService(db_session)
    project = project_service.create_project({
        "name": f"Project {uuid4().hex[:8]}", 
        "client_id": client.id
    })
    
    # Create run
    run_payload = {
        "name": f"Run {uuid4().hex[:8]}",
        "project_id": project.id
    }
    response = auth_client.post("/api/v1/runs/", json=run_payload)
    assert response.status_code == 201
    run_data = response.json()
    assert run_data["name"] == run_payload["name"]
    run_id = run_data["id"]
    
    # Get run
    response = auth_client.get(f"/api/v1/runs/{run_id}")
    assert response.status_code == 200
    assert response.json()["name"] == run_payload["name"]
    
    # List runs by project
    response = auth_client.get(f"/api/v1/runs/project/{project.id}")
    assert response.status_code == 200
    runs = response.json()
    assert len(runs) > 0
    assert any(r["id"] == run_id for r in runs)
    
    # Update run
    updated_payload = {"name": f"Run Updated {uuid4().hex[:8]}"}
    response = auth_client.patch(f"/api/v1/runs/{run_id}", json=updated_payload)
    assert response.status_code == 200
    assert response.json()["name"] == updated_payload["name"]
    
    # Delete run
    response = auth_client.delete(f"/api/v1/runs/{run_id}")
    assert response.status_code == 204
    
    # Verify deletion
    response = auth_client.get(f"/api/v1/runs/{run_id}")
    assert response.status_code == 404


def test_test_suite_crud(auth_client, db_session):
    """Test TestSuite CRUD operations"""
    # Create test suite
    suite_payload = {"name": f"Suite {uuid4().hex[:8]}"}
    response = auth_client.post("/api/v1/test-suites/", json=suite_payload)
    assert response.status_code == 201
    suite_data = response.json()
    assert suite_data["name"] == suite_payload["name"]
    suite_id = suite_data["id"]
    
    # Get test suite
    response = auth_client.get(f"/api/v1/test-suites/{suite_id}")
    assert response.status_code == 200
    assert response.json()["name"] == suite_payload["name"]
    
    # List test suites
    response = auth_client.get("/api/v1/test-suites/")
    assert response.status_code == 200
    suites = response.json()
    assert any(s["id"] == suite_id for s in suites)
    
    # Update test suite
    updated_payload = {"name": f"Suite Updated {uuid4().hex[:8]}"}
    response = auth_client.patch(f"/api/v1/test-suites/{suite_id}", json=updated_payload)
    assert response.status_code == 200
    assert response.json()["name"] == updated_payload["name"]
    
    # Delete test suite
    response = auth_client.delete(f"/api/v1/test-suites/{suite_id}")
    assert response.status_code == 204
    
    # Verify deletion
    response = auth_client.get(f"/api/v1/test-suites/{suite_id}")
    assert response.status_code == 404


def test_scenario_and_status_set_crud(auth_client, db_session):
    """Test Scenario and StatusSet CRUD (needed for TestCase)"""
    from app.services.scenario import ScenarioService
    from app.services.status_set import StatusSetService
    
    # Create scenario
    scenario_service = ScenarioService(db_session)
    scenario = scenario_service.create_scenario({
        "name": f"Scenario {uuid4().hex[:8]}"
    })
    
    # Create status set
    status_set_service = StatusSetService(db_session)
    status_set = status_set_service.create_status_set({
        "name": f"StatusSet {uuid4().hex[:8]}"
    })
    
    assert scenario.id is not None
    assert status_set.id is not None


def test_test_case_crud(auth_client, db_session):
    """Test TestCase CRUD operations"""
    from app.services.scenario import ScenarioService
    from app.services.status_set import StatusSetService
    
    # Create prerequisites
    scenario_service = ScenarioService(db_session)
    scenario = scenario_service.create_scenario({
        "name": f"Scenario {uuid4().hex[:8]}"
    })
    
    status_set_service = StatusSetService(db_session)
    status_set = status_set_service.create_status_set({
        "name": f"StatusSet {uuid4().hex[:8]}"
    })
    
    # Create test case
    case_payload = {
        "scenario_id": scenario.id,
        "status_set_id": status_set.id
    }
    response = auth_client.post("/api/v1/test-cases/", json=case_payload)
    assert response.status_code == 201
    case_data = response.json()
    case_id = case_data["id"]
    
    # Get test case
    response = auth_client.get(f"/api/v1/test-cases/{case_id}")
    assert response.status_code == 200
    assert response.json()["scenario_id"] == scenario.id
    
    # List test cases
    response = auth_client.get("/api/v1/test-cases/")
    assert response.status_code == 200
    cases = response.json()
    assert any(c["id"] == case_id for c in cases)
    
    # Update test case
    response = auth_client.patch(f"/api/v1/test-cases/{case_id}", json={})
    assert response.status_code == 200
    
    # Delete test case
    response = auth_client.delete(f"/api/v1/test-cases/{case_id}")
    assert response.status_code == 204


def test_test_case_version_crud(auth_client, db_session):
    """Test TestCaseVersion CRUD operations"""
    from app.services.scenario import ScenarioService
    from app.services.status_set import StatusSetService
    from app.services.test_case import TestCaseService
    
    # Create prerequisites
    scenario_service = ScenarioService(db_session)
    scenario = scenario_service.create_scenario({
        "name": f"Scenario {uuid4().hex[:8]}"
    })
    
    status_set_service = StatusSetService(db_session)
    status_set = status_set_service.create_status_set({
        "name": f"StatusSet {uuid4().hex[:8]}"
    })
    
    test_case_service = TestCaseService(db_session)
    test_case = test_case_service.create_test_case({
        "scenario_id": scenario.id,
        "status_set_id": status_set.id
    })
    
    # Get current user ID from a db query
    from app.services.users import UserService
    user_service = UserService(db_session)
    # For testing, we'll use a hack to get the current user ID
    from db.models.users import Users
    user = db_session.query(Users).first()
    user_id = user.id if user else 1
    
    # Create test case version
    version_payload = {
        "test_case_id": test_case.id,
        "version": 1,
        "name": "Version 1",
        "description": "Initial version",
        "steps": "Step 1\nStep 2",
        "expected_result": "Success",
        "created_by": user_id
    }
    response = auth_client.post("/api/v1/test-case-versions/", json=version_payload)
    assert response.status_code == 201
    version_data = response.json()
    version_id = version_data["id"]
    
    # Get test case version
    response = auth_client.get(f"/api/v1/test-case-versions/{version_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Version 1"
    
    # List versions by test case
    response = auth_client.get(f"/api/v1/test-case-versions/test-case/{test_case.id}")
    assert response.status_code == 200
    versions = response.json()
    assert any(v["id"] == version_id for v in versions)
    
    # Update test case version
    updated_payload = {"name": "Version 1 Updated"}
    response = auth_client.patch(f"/api/v1/test-case-versions/{version_id}", json=updated_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Version 1 Updated"
    
    # Delete test case version
    response = auth_client.delete(f"/api/v1/test-case-versions/{version_id}")
    assert response.status_code == 204


def test_suitcase_crud(auth_client, db_session):
    """Test Suitcase CRUD operations"""
    from app.services.scenario import ScenarioService
    from app.services.status_set import StatusSetService
    from app.services.test_case import TestCaseService
    from app.services.test_suite import TestSuiteService
    
    # Create prerequisites
    scenario_service = ScenarioService(db_session)
    scenario = scenario_service.create_scenario({
        "name": f"Scenario {uuid4().hex[:8]}"
    })
    
    status_set_service = StatusSetService(db_session)
    status_set = status_set_service.create_status_set({
        "name": f"StatusSet {uuid4().hex[:8]}"
    })
    
    test_case_service = TestCaseService(db_session)
    test_case = test_case_service.create_test_case({
        "scenario_id": scenario.id,
        "status_set_id": status_set.id
    })
    
    test_suite_service = TestSuiteService(db_session)
    test_suite = test_suite_service.create_test_suite({
        "name": f"Suite {uuid4().hex[:8]}"
    })
    
    # Create suitcase
    suitcase_payload = {
        "test_case_id": test_case.id,
        "test_suite_id": test_suite.id
    }
    response = auth_client.post("/api/v1/suitcases/", json=suitcase_payload)
    assert response.status_code == 201
    suitcase_data = response.json()
    suitcase_id = suitcase_data["id"]
    
    # Get suitcase
    response = auth_client.get(f"/api/v1/suitcases/{suitcase_id}")
    assert response.status_code == 200
    
    # List suitcases by test case
    response = auth_client.get(f"/api/v1/suitcases/test-case/{test_case.id}")
    assert response.status_code == 200
    suitcases = response.json()
    assert any(s["id"] == suitcase_id for s in suitcases)
    
    # List suitcases by test suite
    response = auth_client.get(f"/api/v1/suitcases/test-suite/{test_suite.id}")
    assert response.status_code == 200
    suitcases = response.json()
    assert any(s["id"] == suitcase_id for s in suitcases)
    
    # Update suitcase
    response = auth_client.patch(f"/api/v1/suitcases/{suitcase_id}", json={})
    assert response.status_code == 200
    
    # Delete suitcase
    response = auth_client.delete(f"/api/v1/suitcases/{suitcase_id}")
    assert response.status_code == 204
