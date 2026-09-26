"""Extracted financial line items, one row per metric per fiscal period."""
import uuid

from sqlalchemy import Column, Float, ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import relationship

from app.db.base import Base


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    metric_name = Column(String(80), nullable=False, index=True)
    value = Column(Float, nullable=True)
    unit = Column(String(20), default="INR_CR", nullable=False)
    fiscal_year = Column(Integer, nullable=True)
    fiscal_period = Column(String(10), nullable=True)
    source_page = Column(Integer, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)

    document = relationship("Document", back_populates="metrics")

    __table_args__ = (
        Index(
            "ix_metrics_doc_name_period",
            "document_id",
            "metric_name",
            "fiscal_year",
            "fiscal_period",
        ),
    )

    def __repr__(self) -> str:
        return f"<FinancialMetric {self.metric_name}={self.value} {self.unit}>"