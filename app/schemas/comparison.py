"""Multi-document comparison schemas (Sprint 3)."""
from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CompareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_ids: List[UUID] = Field(..., min_length=2, max_length=5)
    metric_names: List[str] = Field(default_factory=list)


class DeltaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metric_name: str
    values: Dict[str, float]  # document_id -> value
    absolute_delta: float
    percent_delta: float


class ComparisonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_ids: List[UUID]
    deltas: List[DeltaItem]