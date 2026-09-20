"""Shared pytest fixtures for backend tests."""
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.api.deps import get_current_user_id
from app.db.session import get_db
from app.main import app
from app.models import Base

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test_financial.db",  # Fallback for fast unit tests
)

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


@pytest.fixture(scope="session")
def test_engine():
    if TEST_DB_URL.startswith("sqlite"):
        engine = create_engine(
            TEST_DB_URL,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
    else:
        engine = create_engine(TEST_DB_URL, poolclass=NullPool)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    from uuid import UUID

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_user_id():
        return UUID(DEMO_USER_ID)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = override_user_id
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Minimal PDF magic-bytes payload for upload tests."""
    return b"%PDF-1.4\n%fake pdf body\n%%EOF"