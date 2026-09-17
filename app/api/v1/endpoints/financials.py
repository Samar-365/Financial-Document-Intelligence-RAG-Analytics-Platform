"""Endpoints #6–#8: metrics, ratios, health score."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import DocumentNotFoundException
from app.models.analysis_result import AnalysisResult
from app.models.document import Document
from app.models.financial_metric import FinancialMetric
from app.schemas.comparison import CompareRequest, ComparisonResponse
from app.schemas.financial import (
    FinancialMetricItem,
    FinancialMetricsResponse,
    FinancialRatiosResponse,
    HealthScoreResponse,
)
from app.services.comparison_service import compare_documents

router = APIRouter(tags=["financials"])


def _ensure_document(db: Session, document_id: UUID) -> Document:
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise DocumentNotFoundException(str(document_id))
    return doc


@router.get(
    "/financial-metrics/{document_id}",
    response_model=FinancialMetricsResponse,
)
async def get_financial_metrics(
    document_id: UUID,
    db: Session = Depends(get_db),
) -> FinancialMetricsResponse:
    _ensure_document(db, document_id)
    rows = (
        db.query(FinancialMetric)
        .filter(FinancialMetric.document_id == document_id)
        .all()
    )
    return FinancialMetricsResponse(
        document_id=document_id,
        metrics=[FinancialMetricItem.model_validate(r) for r in rows],
    )


@router.get(
    "/financial-ratios/{document_id}",
    response_model=FinancialRatiosResponse,
)
async def get_financial_ratios(
    document_id: UUID,
    db: Session = Depends(get_db),
) -> FinancialRatiosResponse:
    _ensure_document(db, document_id)
    analysis = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.document_id == document_id)
        .first()
    )
    if not analysis:
        return FinancialRatiosResponse(document_id=document_id)
    return FinancialRatiosResponse(
        document_id=document_id,
        opm=analysis.opm,
        npm=analysis.npm,
        roe=analysis.roe,
        roce=analysis.roce,
        current_ratio=analysis.current_ratio,
        quick_ratio=analysis.quick_ratio,
        debt_to_equity=analysis.debt_to_equity,
        interest_coverage=analysis.interest_coverage,
    )


@router.get(
    "/health-score/{document_id}",
    response_model=HealthScoreResponse,
)
async def get_health_score(
    document_id: UUID,
    db: Session = Depends(get_db),
) -> HealthScoreResponse:
    _ensure_document(db, document_id)
    analysis = (
        db.query(AnalysisResult)
        .filter(AnalysisResult.document_id == document_id)
        .first()
    )
    if not analysis:
        return HealthScoreResponse(
            document_id=document_id,
            overall_score=0.0,
            growth_score=0.0,
            profitability_score=0.0,
            liquidity_score=0.0,
            leverage_score=0.0,
            cash_flow_score=0.0,
        )
    return HealthScoreResponse(
        document_id=document_id,
        overall_score=analysis.overall_score or 0.0,
        growth_score=analysis.growth_score or 0.0,
        profitability_score=analysis.profitability_score or 0.0,
        liquidity_score=analysis.liquidity_score or 0.0,
        leverage_score=analysis.leverage_score or 0.0,
        cash_flow_score=analysis.cash_flow_score or 0.0,
        risk_flags=list(analysis.risk_flags or []),
    )


@router.post(
    "/compare",
    response_model=ComparisonResponse,
)
async def compare_financial_documents(
    payload: CompareRequest,
    db: Session = Depends(get_db),
) -> ComparisonResponse:
    for doc_id in payload.document_ids:
        _ensure_document(db, doc_id)
    return compare_documents(db, payload.document_ids, payload.metric_names)