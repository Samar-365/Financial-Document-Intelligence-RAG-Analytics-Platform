"""RAG query request and response schemas."""
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

FORBIDDEN_PATTERNS = [
    "<context>", "</context>", "IGNORE PREVIOUS", "SYSTEM:", "<|system|>",
]


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    document_id: UUID
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)

    @field_validator("question")
    @classmethod
    def sanitize_question(cls, v: str) -> str:
        lowered = v.lower()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.lower() in lowered:
                raise ValueError(f"Forbidden pattern detected: {pattern}")
        return v.strip()


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    page_number: int = Field(..., ge=1)
    snippet: str = Field(..., max_length=500)
    relevance_score: float = Field(..., ge=0.0, le=1.0)


class RAGResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    citations: List[Citation] = []
    latency_ms: int = 0
    model_used: str = "unknown"