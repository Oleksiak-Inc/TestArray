import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

load_dotenv(REPO_ROOT / ".env")

from app import create_app
from db.base import Base
import db.models  # Ensure SQLAlchemy models are imported before metadata creation
import db.session as db_session_module
import core.startup as startup_module
from db.session import get_db

SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

db_session_module.SessionLocal = TestingSessionLocal
startup_module.SessionLocal = TestingSessionLocal

Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def app():
    app = create_app()
    return app


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(app, db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def auth_client(client):
    email = f"test-{uuid4().hex}@example.com"
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

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    client.cookies.update(login_resp.cookies)
    return client
