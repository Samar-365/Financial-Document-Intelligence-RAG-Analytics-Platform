"""Financial metric, ratio, and health-score response schemas."""
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FinancialMetricItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    metric_name: str
    value: Optional[float] = None
    unit: str
    fiscal_year: Optional[int] = None
    fiscal_period: Optional[str] = None
    source_page: Optional[int] = None
    confidence: float = 1.0


class FinancialMetricsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    metrics: List[FinancialMetricItem]


class FinancialRatiosResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    opm: Optional[float] = None
    npm: Optional[float] = None
    roe: Optional[float] = None
    roce: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    interest_coverage: Optional[float] = None


class HealthScoreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    overall_score: float = Field(..., ge=0.0, le=100.0)
    growth_score: float = Field(..., ge=0.0, le=100.0)
    profitability_score: float = Field(..., ge=0.0, le=100.0)
    liquidity_score: float = Field(..., ge=0.0, le=100.0)
    leverage_score: float = Field(..., ge=0.0, le=100.0)
    cash_flow_score: float = Field(..., ge=0.0, le=100.0)
    risk_flags: List[str] = []