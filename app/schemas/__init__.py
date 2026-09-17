"""Pydantic request and response schemas for REST API validation."""
from app.schemas.common import ErrorDetail, ResponseEnvelope
from app.schemas.comparison import ComparisonResponse, CompareRequest, DeltaItem
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.schemas.error import ErrorResponse
from app.schemas.financial import (
    FinancialMetricItem,
    FinancialMetricsResponse,
    FinancialRatiosResponse,
    HealthScoreResponse,
)
from app.schemas.query import Citation, QueryRequest, RAGResponse

__all__ = [
    "ErrorDetail",
    "ResponseEnvelope",
    "CompareRequest",
    "ComparisonResponse",
    "DeltaItem",
    "DocumentResponse",
    "DocumentUploadResponse",
    "DocumentListResponse",
    "ErrorResponse",
    "FinancialMetricItem",
    "FinancialMetricsResponse",
    "FinancialRatiosResponse",
    "HealthScoreResponse",
    "Citation",
    "QueryRequest",
    "RAGResponse",
]