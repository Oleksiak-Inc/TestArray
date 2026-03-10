from datetime import datetime

import pytest


def test_register_and_login_and_me_and_logout(client):
    # Register a new user.
    email = f"test-{datetime.utcnow().timestamp()}@example.com"
    password = "test-password"

    register_resp = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": password,
        },
    )
    assert register_resp.status_code == 200
    assert register_resp.json()["email"] == email

    # Login with the new user and make sure we get a session cookie.
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_resp.status_code == 200
    assert "session" in login_resp.cookies

    # Use the session cookie to hit /me.
    client.cookies.update(login_resp.cookies)
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == email

    # Logout (should clear the cookie server-side and in the TestClient). 
    logout_resp = client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200
    assert "session" not in logout_resp.cookies


def test_login_invalid_credentials(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "doesnotexist@example.com", "password": "x"},
    )
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
