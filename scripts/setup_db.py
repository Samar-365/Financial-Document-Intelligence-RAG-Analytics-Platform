"""Database Setup and Migration Initialization Script for PostgreSQL."""

import os
import sys
from pathlib import Path
from sqlalchemy import text

# Ensure project root is in path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import engine, Base
from app.models import (
    user,
    document,
    document_chunk,
    financial_metric,
    analysis_result,
)


def init_database():
    """Initializes PostgreSQL database schema and pgvector extension."""
    print(f"Connecting to PostgreSQL database at {engine.url}...")
    try:
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
                print("[OK] PostgreSQL pgvector extension verified.")
            except Exception as e:
                print(f"[!] pgvector extension note: {e}")
    except Exception as exc:
        print(f"\n[ERROR] PostgreSQL connection failed: {exc}")
        print("Please ensure PostgreSQL Alpine container is running and DATABASE_URL is configured.")
        sys.exit(1)

    print("Creating database schema tables via SQLAlchemy ORM...")
    Base.metadata.create_all(bind=engine)
    print("[OK] All database tables successfully initialized on PostgreSQL.")
    return engine


if __name__ == "__main__":
    init_database()
