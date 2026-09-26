"""Database Seeding Script for Demo and Development Environments."""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.financial_metric import FinancialMetric
from app.models.analysis_result import AnalysisResult

DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DOC_2025_ID = uuid.UUID("11111111-1111-1111-1111-111111112025")
DOC_2024_ID = uuid.UUID("22222222-2222-2222-2222-222222222024")


from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

def seed_database():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
    except Exception as exc:
        print(f"[!] Primary DB connection failed ({exc}). Falling back to SQLite...")
        sqlite_engine = create_engine("sqlite:///./financial_rag.db", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=sqlite_engine)
        FallbackSession = sessionmaker(bind=sqlite_engine)
        db = FallbackSession()

    try:
        print("Seeding database with demo financial records...")

        # 1. Ensure Demo User
        user = db.query(User).filter(User.id == DEMO_USER_ID).first()
        if not user:
            user = User(
                id=DEMO_USER_ID,
                email="analyst@finintel.ai",
                full_name="Senior Financial Analyst",
                hashed_password="mock_hashed_pw",
                is_active=True,
            )
            db.add(user)
            db.commit()
            print("[OK] Demo User created.")

        # 2. Seed Document FY2025
        doc_2025 = db.query(Document).filter(Document.id == DOC_2025_ID).first()
        if not doc_2025:
            doc_2025 = Document(
                id=DOC_2025_ID,
                user_id=DEMO_USER_ID,
                filename="ABC_AR_2025.pdf",
                file_hash="hash_abc_ar_2025_mock",
                file_size_bytes=4520100,
                page_count=180,
                status="PROCESSED",
            )
            db.add(doc_2025)

            # Sample Chunks
            chunks = [
                DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=DOC_2025_ID,
                    chunk_id=str(uuid.uuid4()),
                    chunk_index=0,
                    page_number=87,
                    content="Total Revenue from Operations stood at ₹11,450 Cr for the financial year ending March 31, 2025, an increase of 12.25% YoY.",
                    token_estimate=32,
                    is_table_chunk=False,
                    embedding=[0.01] * 384,
                ),
                DocumentChunk(
                    id=uuid.uuid4(),
                    document_id=DOC_2025_ID,
                    chunk_id=str(uuid.uuid4()),
                    chunk_index=1,
                    page_number=42,
                    content="Management Discussion: Domestic demand surged across all business units. Total Debt was successfully reduced to ₹3,900 Cr.",
                    token_estimate=28,
                    is_table_chunk=False,
                    embedding=[0.02] * 384,
                ),
            ]
            db.add_all(chunks)

            # Metrics
            metrics_2025 = [
                FinancialMetric(document_id=DOC_2025_ID, metric_name="Revenue", value=11450.0, unit="Cr", fiscal_year=2025, confidence=0.99, source_page=87),
                FinancialMetric(document_id=DOC_2025_ID, metric_name="Gross Profit", value=4580.0, unit="Cr", fiscal_year=2025, confidence=0.97, source_page=87),
                FinancialMetric(document_id=DOC_2025_ID, metric_name="EBITDA", value=2340.0, unit="Cr", fiscal_year=2025, confidence=0.95, source_page=88),
                FinancialMetric(document_id=DOC_2025_ID, metric_name="Net Income", value=1410.0, unit="Cr", fiscal_year=2025, confidence=0.98, source_page=88),
                FinancialMetric(document_id=DOC_2025_ID, metric_name="Total Debt", value=3900.0, unit="Cr", fiscal_year=2025, confidence=0.98, source_page=95),
                FinancialMetric(document_id=DOC_2025_ID, metric_name="Cash & Equivalents", value=2150.0, unit="Cr", fiscal_year=2025, confidence=0.97, source_page=95),
                FinancialMetric(document_id=DOC_2025_ID, metric_name="Operating Cash Flow", value=2680.0, unit="Cr", fiscal_year=2025, confidence=0.98, source_page=102),
            ]
            db.add_all(metrics_2025)

            # Analysis Result
            analysis_2025 = AnalysisResult(
                id=uuid.uuid4(),
                document_id=DOC_2025_ID,
                opm=20.44,
                npm=12.31,
                roe=16.21,
                roce=18.45,
                current_ratio=1.65,
                quick_ratio=1.20,
                debt_to_equity=0.45,
                interest_coverage=6.20,
                overall_score=78.0,
                growth_score=86.0,
                profitability_score=82.0,
                liquidity_score=71.0,
                leverage_score=74.0,
                cash_flow_score=77.0,
                risk_flags=["Interest Rate Sensitivity", "Environmental Compliance FY27"],
            )
            db.add(analysis_2025)
            print("[OK] FY2025 Document and Metrics seeded.")

        # 3. Seed Document FY2024
        doc_2024 = db.query(Document).filter(Document.id == DOC_2024_ID).first()
        if not doc_2024:
            doc_2024 = Document(
                id=DOC_2024_ID,
                user_id=DEMO_USER_ID,
                filename="ABC_AR_2024.pdf",
                file_hash="hash_abc_ar_2024_mock",
                file_size_bytes=4210000,
                page_count=172,
                status="PROCESSED",
            )
            db.add(doc_2024)

            metrics_2024 = [
                FinancialMetric(document_id=DOC_2024_ID, metric_name="Revenue", value=10200.0, unit="Cr", fiscal_year=2024, confidence=0.99, source_page=85),
                FinancialMetric(document_id=DOC_2024_ID, metric_name="EBITDA", value=2100.0, unit="Cr", fiscal_year=2024, confidence=0.96, source_page=86),
                FinancialMetric(document_id=DOC_2024_ID, metric_name="Net Income", value=1200.0, unit="Cr", fiscal_year=2024, confidence=0.98, source_page=86),
                FinancialMetric(document_id=DOC_2024_ID, metric_name="Total Debt", value=4200.0, unit="Cr", fiscal_year=2024, confidence=0.97, source_page=92),
                FinancialMetric(document_id=DOC_2024_ID, metric_name="Cash & Equivalents", value=1800.0, unit="Cr", fiscal_year=2024, confidence=0.96, source_page=92),
            ]
            db.add_all(metrics_2024)


            analysis_2024 = AnalysisResult(
                id=uuid.uuid4(),
                document_id=DOC_2024_ID,
                opm=18.50,
                npm=11.76,
                roe=14.80,
                roce=16.10,
                current_ratio=1.52,
                quick_ratio=1.10,
                debt_to_equity=0.55,
                interest_coverage=5.40,
                overall_score=72.0,
                growth_score=78.0,
                profitability_score=76.0,
                liquidity_score=68.0,
                leverage_score=69.0,
                cash_flow_score=71.0,
                risk_flags=["Supply Chain Bottlenecks", "Foreign Exchange Volatility"],
            )
            db.add(analysis_2024)
            print("[OK] FY2024 Document and Metrics seeded.")

        db.commit()
        print("[OK] Database seeding successfully finished.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
