from uuid import uuid4


def test_client_and_project_crud(auth_client):
    client_payload = {"name": f"Client {uuid4().hex[:8]}"}
    client_response = auth_client.post("/api/v1/clients/", json=client_payload)
    assert client_response.status_code == 201
    client_data = client_response.json()
    assert client_data["name"] == client_payload["name"]
    client_id = client_data["id"]

    get_client_response = auth_client.get(f"/api/v1/clients/{client_id}")
    assert get_client_response.status_code == 200
    assert get_client_response.json()["name"] == client_payload["name"]

    updated_name = f"Updated {uuid4().hex[:8]}"
    patch_client_response = auth_client.patch(
        f"/api/v1/clients/{client_id}", json={"name": updated_name}
    )
    assert patch_client_response.status_code == 200
    assert patch_client_response.json()["name"] == updated_name

    project_payload = {"name": f"Project {uuid4().hex[:8]}", "client_id": client_id}
    project_response = auth_client.post("/api/v1/projects/", json=project_payload)
    assert project_response.status_code == 201
    project_data = project_response.json()
    assert project_data["name"] == project_payload["name"]
    assert project_data["client_id"] == client_id
    project_id = project_data["id"]

    get_project_response = auth_client.get(f"/api/v1/projects/{project_id}")
    assert get_project_response.status_code == 200
    assert get_project_response.json()["name"] == project_payload["name"]
    assert get_project_response.json()["client_id"] == client_id

    get_project_with_client_response = auth_client.get(f"/api/v1/projects/{project_id}/with-client")
    assert get_project_with_client_response.status_code == 200
    assert get_project_with_client_response.json()["client_id"] == client_id

    updated_project_name = f"Project {uuid4().hex[:8]}"
    patch_project_response = auth_client.patch(
        f"/api/v1/projects/{project_id}", json={"name": updated_project_name}
    )
    assert patch_project_response.status_code == 200
    assert patch_project_response.json()["name"] == updated_project_name
