"""Shared response envelope and pagination schemas."""
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    path: Optional[str] = None
    details: Optional[list] = None


class ResponseEnvelope(BaseModel, Generic[T]):
    """Uniform response wrapper for all endpoints."""

    model_config = ConfigDict(extra="forbid")

    data: Optional[T] = None
    error: Optional[ErrorDetail] = None
    meta: Optional[dict] = None


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int