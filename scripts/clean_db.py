"""Script to wipe all mock and development data, ensuring a clean dynamic database state."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.core.database import SessionLocal, engine
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.financial_metric import FinancialMetric
from app.models.analysis_result import AnalysisResult
from app.models.user import User

def clean_database():
    print("[*] Connecting to database to wipe all mock and development records...")
    db = SessionLocal()
    try:
        # Check connection
        db.execute(text("SELECT 1"))
        
        # Truncate tables with CASCADE
        tables = [
            "analysis_results",
            "financial_metrics",
            "document_chunks",
            "documents",
            "audit_logs",
        ]
        
        for table in tables:
            try:
                db.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
                print(f"  ✓ Cleaned table: {table}")
            except Exception as e:
                # Table might not exist yet or non-Postgres
                db.rollback()
                print(f"  ! Note on table {table}: {e}")

        # Ensure demo user exists with 0 documents for API auth testing
        from uuid import UUID
        DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
        user = db.query(User).filter(User.id == DEMO_USER_ID).first()
        if not user:
            user = User(
                id=DEMO_USER_ID,
                email="analyst@finintel.ai",
                full_name="Financial Analyst",
                hashed_password="hashed_secure_password",
                is_active=True,
            )
            db.add(user)
        
        db.commit()
        
        doc_count = db.query(Document).count()
        chunk_count = db.query(DocumentChunk).count()
        metric_count = db.query(FinancialMetric).count()
        analysis_count = db.query(AnalysisResult).count()
        
        print(f"[OK] Database wiped clean successfully!")
        print(f"     Documents: {doc_count} (expected 0)")
        print(f"     Chunks:    {chunk_count} (expected 0)")
        print(f"     Metrics:   {metric_count} (expected 0)")
        print(f"     Analyses:  {analysis_count} (expected 0)")
        
    except Exception as exc:
        db.rollback()
        print(f"[ERROR] Failed to clean database: {exc}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    clean_database()
