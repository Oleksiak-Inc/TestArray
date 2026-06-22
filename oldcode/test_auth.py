from uuid import uuid4


def test_register_login_me_and_logout(client):
    email = f"test-{uuid4().hex}@example.com"
    password = "test-password"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 200
    assert register_response.json()["email"] == email

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )

    assert login_response.status_code == 200
    assert "session" in login_response.cookies

    client.cookies.update(login_response.cookies)
    me_response = client.get("/api/v1/auth/me")

    assert me_response.status_code == 200
    assert me_response.json()["email"] == email

    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 200
    assert "session" not in logout_response.cookies


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "doesnotexist@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_me_requires_auth(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
