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
        from sqlalchemy import event
        engine = create_engine(
            TEST_DB_URL,
            connect_args={"check_same_thread": False},
            poolclass=NullPool,
        )
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    else:
        engine = create_engine(TEST_DB_URL, poolclass=NullPool)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    from uuid import UUID
    from app.models.user import User

    connection = test_engine.connect()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    try:
        # Clear all tables between tests for clean test isolation
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()

        # Seed the authenticated demo user
        demo_user = User(
            id=UUID(DEMO_USER_ID),
            email="test@finintel.ai",
            full_name="Test User",
            is_active=True,
        )
        session.add(demo_user)
        session.commit()

        yield session
    finally:
        session.close()
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