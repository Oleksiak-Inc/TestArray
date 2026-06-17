from uuid import uuid4

from app.services.client import ClientService
from app.services.project import ProjectService
from db.models.clients import Clients
from db.models.projects import Projects


def test_client_service_create_and_update(db_session):
    service = ClientService(db_session)
    client_data = {"name": f"Client {uuid4().hex[:8]}"}
    client = service.create_client(client_data)

    assert isinstance(client, Clients)
    assert client.name == client_data["name"]

    updated_name = f"Client Updated {uuid4().hex[:8]}"
    updated_client = service.update_client(client.id, {"name": updated_name})

    assert isinstance(updated_client, Clients)
    assert updated_client.name == updated_name


def test_project_service_create_and_update(db_session):
    client_service = ClientService(db_session)
    client = client_service.create_client({"name": f"Client {uuid4().hex[:8]}"})

    service = ProjectService(db_session)
    project_data = {"name": f"Project {uuid4().hex[:8]}", "client_id": client.id}
    project = service.create_project(project_data)

    assert isinstance(project, Projects)
    assert project.name == project_data["name"]
    assert project.client_id == client.id

    updated_name = f"Project Updated {uuid4().hex[:8]}"
    updated_project = service.update_project(project.id, {"name": updated_name})

    assert isinstance(updated_project, Projects)
    assert updated_project.name == updated_name
