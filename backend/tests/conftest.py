import os
import sys

import pytest

# Ensure the backend package directory is on sys.path when pytest runs from the repo root.
HERE = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(HERE, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from fastapi.testclient import TestClient

from app import create_app
from db.base import Base
from db.engine import engine
from db.session import SessionLocal, get_db


@pytest.fixture(scope="session")
def app():
    """Create a FastAPI app and ensure the database schema is present."""
    # Ensure schema exists before tests run.
    Base.metadata.create_all(bind=engine)

    app = create_app()
    yield app

    # Tear down schema after tests.
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provide a database session that is rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()

    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(app, db_session):
    """FastAPI test client that uses a transactional DB session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
