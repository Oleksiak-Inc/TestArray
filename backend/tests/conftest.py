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
from helpers import _uid

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
def auth_client(client, db_session):
    # Create a registered (non-admin) user via the API and return a logged-in client.
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
    # Create a user and assign them to a group that has all global permissions.
    from core.security import PasswordHasher
    from core.permissions import PERMISSIONS
    from db.models.permissions import Permissions
    from db.models.user_groups import UserGroups
    from db.models.group_permissions import GroupPermissions
    from db.models.groups_members import GroupsMembers
    from db.models.users import Users

    # Ensure permissions are seeded
    for code, description, scope in PERMISSIONS:
        existing = db_session.query(Permissions).filter(Permissions.code == code).first()
        if not existing:
            db_session.add(Permissions(code=code, description=description, scope=scope))
    db_session.flush()

    # Ensure superadmin group exists and has all global perms
    group = db_session.query(UserGroups).filter(UserGroups.name == "superadmin").first()
    if not group:
        # create a temp owner user to satisfy FK; owner will be updated after creating admin_user
        temp_owner = Users(first_name="Owner", last_name="User", email=f"owner-{uuid4().hex}@example.com", password=PasswordHasher.hash("owner-pass"))
        db_session.add(temp_owner)
        db_session.flush()
        group = UserGroups(name="superadmin", owner_id=temp_owner.id, created_by_id=temp_owner.id)
        db_session.add(group)
        db_session.flush()

    # Grant the superadmin group every permission (global and local) for tests
    all_global_perms = db_session.query(Permissions).all()
    existing_gp_ids = {gp.permission_id for gp in group.group_permissions}
    for perm in all_global_perms:
        if perm.id not in existing_gp_ids:
            db_session.add(GroupPermissions(group_id=group.id, permission_id=perm.id))

    db_session.flush()

    # create the admin user and add membership to the superadmin group
    email = f"admin-{uuid4().hex}@example.com"
    password = "admin-password"
    admin_user = Users(first_name="Admin", last_name="User", email=email, password=PasswordHasher.hash(password), active=True)
    db_session.add(admin_user)
    db_session.flush()

    membership = db_session.query(GroupsMembers).filter(GroupsMembers.group_id == group.id, GroupsMembers.user_id == admin_user.id).first()
    if not membership:
        db_session.add(GroupsMembers(group_id=group.id, user_id=admin_user.id))

    db_session.commit()

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    client.cookies.update(login_resp.cookies)
    return client


# ---------------------------------------------------------------------------
# Shared test fixtures (migrated from test_full_suite.py)
# ---------------------------------------------------------------------------


@pytest.fixture
def make_client(db_session):
    """Return a factory that creates a Clients row via the service layer."""
    from app.services.client import ClientService

    def _factory(name: str | None = None) -> object:
        return ClientService(db_session).create_client(
            {"name": name or f"Client-{_uid()}"}
        )

    return _factory


@pytest.fixture
def make_project(db_session, make_client):
    """Return a factory that creates a Projects row via the service layer."""
    from app.services.project import ProjectService

    def _factory(client=None, name: str | None = None) -> object:
        if client is None:
            client = make_client()
        return ProjectService(db_session).create_project(
            {"name": name or f"Project-{_uid()}", "client_id": client.id}
        )

    return _factory


@pytest.fixture
def make_scenario(db_session):
    from app.services.scenario import ScenarioService

    def _factory(name: str | None = None) -> object:
        return ScenarioService(db_session).create_scenario(
            {"name": name or f"Scenario-{_uid()}"}
        )

    return _factory


@pytest.fixture
def make_status_set(db_session):
    from app.services.status_set import StatusSetService

    def _factory(name: str | None = None) -> object:
        return StatusSetService(db_session).create_status_set(
            {"name": name or f"StatusSet-{_uid()}"}
        )

    return _factory


@pytest.fixture
def make_test_case(db_session, make_scenario, make_status_set):
    from app.services.test_case import TestCaseService

    def _factory(scenario=None, status_set=None) -> object:
        s = scenario or make_scenario()
        ss = status_set or make_status_set()
        return TestCaseService(db_session).create_test_case(
            {"scenario_id": s.id, "status_set_id": ss.id}
        )

    return _factory


@pytest.fixture
def make_test_suite(db_session):
    from app.services.test_suite import TestSuiteService

    def _factory(name: str | None = None) -> object:
        return TestSuiteService(db_session).create_test_suite(
            {"name": name or f"Suite-{_uid()}"}
        )

    return _factory


@pytest.fixture
def current_user(auth_client, db_session):
    """Return the Users row that auth_client registered and logged in as.

    Depends on auth_client so the user is guaranteed to exist before we query.
    """
    from db.models.users import Users

    return db_session.query(Users).first()
