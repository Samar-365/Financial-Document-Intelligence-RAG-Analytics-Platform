"""Derived analysis: 8 ratios, 5D health scores, risk flags."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, JSON, String, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from app.db.base import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # ── 8 ratios ────────────────────────────────────────────
    opm = Column(Float, nullable=True)
    npm = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    roce = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)
    quick_ratio = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    interest_coverage = Column(Float, nullable=True)

    # ── 5D health scores (0–100) ────────────────────────────
    overall_score = Column(Float, nullable=True)
    growth_score = Column(Float, nullable=True)
    profitability_score = Column(Float, nullable=True)
    liquidity_score = Column(Float, nullable=True)
    leverage_score = Column(Float, nullable=True)
    cash_flow_score = Column(Float, nullable=True)

    # ── 7-domain risk flags ─────────────────────────────────
    risk_flags = Column(JSON().with_variant(ARRAY(String), "postgresql"), default=list, nullable=False)

    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="analysis")

    __table_args__ = (Index("ix_analysis_document", "document_id"),)

    def __repr__(self) -> str:
        return f"<AnalysisResult doc={self.document_id} overall={self.overall_score}>"