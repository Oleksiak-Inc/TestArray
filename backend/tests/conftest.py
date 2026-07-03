import os
import shutil
import sys
import tempfile
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

os.environ["ENVIRONMENT"] = "test"
load_dotenv(REPO_ROOT / ".env.test")

UPLOAD_DIR = Path(tempfile.mkdtemp(prefix="testarray-uploads-"))
os.environ["UPLOAD_DIR"] = str(UPLOAD_DIR)


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_uploads():
    """Remove temporary upload artifacts created during the test session."""
    yield
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR, ignore_errors=True)


from app import create_app
from db.base import Base
import db.models  # Ensure SQLAlchemy models are imported before metadata creation
import db.session as db_session_module
import core.startup as startup_module
from db.session import get_db

TEST_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
engine = create_engine(
    TEST_DATABASE_URL,
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


@pytest.fixture
def admin_client(client, db_session):
    from app.api.utils.auth import hash_password
    from db.models.user_types import UserTypes
    from db.models.users import Users

    admin_type = db_session.query(UserTypes).filter(UserTypes.name == "admin").first()
    if not admin_type:
        admin_type = UserTypes(name="admin", description="Admin user")
        db_session.add(admin_type)
        db_session.commit()
        db_session.refresh(admin_type)

    regular_type = db_session.query(UserTypes).filter(UserTypes.name == "regular").first()
    if not regular_type:
        regular_type = UserTypes(name="regular", description="Regular user")
        db_session.add(regular_type)
        db_session.commit()
        db_session.refresh(regular_type)

    email = f"admin-{uuid4().hex}@example.com"
    password = "admin-password"

    admin_user = Users(
        first_name="Admin",
        last_name="User",
        email=email,
        password=hash_password(password),
        user_type_id=regular_type.id,
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    admin_user.user_type_id = admin_type.id
    db_session.commit()
    db_session.refresh(admin_user)

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    client.cookies.update(login_resp.cookies)
    return client
