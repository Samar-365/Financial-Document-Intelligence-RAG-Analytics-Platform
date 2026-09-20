"""Document upload and retrieval schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(..., min_length=1, max_length=255)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    filename: str
    file_hash: str
    file_size_bytes: Optional[int] = None
    page_count: Optional[int] = None
    status: str
    company_name: Optional[str] = None
    fiscal_year: Optional[int] = None
    fiscal_period: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    filename: str
    status: str
    message: str


class DocumentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int