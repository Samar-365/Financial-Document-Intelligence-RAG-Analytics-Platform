"""Application core database engine, session factory, and declarative base.

Provides:
1. SQLAlchemy engine from DATABASE_URL environment variable.
2. SessionLocal scoped session maker for request-level transactions.
3. get_db() generator for FastAPI dependency injection.
4. Base declarative base for all ORM models.
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base


from app.core.config import settings


def _get_database_url() -> str:
    """Returns the database connection URL from settings (.env)."""
    return settings.DATABASE_URL


_db_url = _get_database_url()
if _db_url.startswith("sqlite"):
    engine = create_engine(
        _db_url,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(
        _db_url,
        pool_pre_ping=True, #Validates connections before checkout to avoid stale TCP sockets
        pool_size=5, #Maintains 5 persistent connections for concurrent query serving
        max_overflow=10, #Allows up to 10 additional connections during traffic spikes
        echo=False, #Set True to log all SQL statements for debugging
    )


# Session factory — each call produces an independent database session
SessionLocal = sessionmaker(
    autocommit=False, #Requires explicit session.commit() for transactional safety
    autoflush=False, #Disables auto-flush to give explicit control over when SQL is emitted
    bind=engine,
)

from app.db.base import Base


def get_db() -> Generator[Session, None, None]: #FastAPI dependency injection generator yielding one session per request
    """Yields a SQLAlchemy session for a single request lifecycle.

    Usage in FastAPI:
        @app.get("/endpoint")
        def handler(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() #Always closes the session even if the request handler raises an exception
