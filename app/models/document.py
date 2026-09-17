"""Uploaded financial document metadata."""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True, index=True)
    file_size_bytes = Column(Integer, nullable=True)
    page_count = Column(Integer, nullable=True)
    status = Column(String(20), default="UPLOADED", nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=True)
    fiscal_period = Column(String(10), nullable=True)  # Q1, Q2, Q3, Q4, FY
    company_name = Column(String(255), nullable=True)
    error_message = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    owner = relationship("User", back_populates="documents")
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    metrics = relationship(
        "FinancialMetric",
        back_populates="document",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    analysis = relationship(
        "AnalysisResult",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_documents_user_created", "user_id", "created_at"),
        Index(
            "ix_documents_company_period",
            "company_name",
            "fiscal_year",
            "fiscal_period",
        ),
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} filename={self.filename} status={self.status}>"