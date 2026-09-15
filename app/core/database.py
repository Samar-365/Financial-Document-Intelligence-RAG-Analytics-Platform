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


def _get_database_url() -> str: #Reads DATABASE_URL from environment with a sensible default
    """Returns the database connection URL from environment configuration."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/financial_rag_db",
    )


# SQLAlchemy engine — connection pool to PostgreSQL
engine = create_engine(
    _get_database_url(),
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

# Declarative base — all ORM models inherit from this
Base = declarative_base()


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
