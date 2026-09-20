"""Service for comparative financial analytics across multiple documents (Sprint 3)."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.financial_metric import FinancialMetric
from app.schemas.comparison import ComparisonResponse, DeltaItem


def compare_documents(
    db: Session,
    document_ids: List[UUID],
    metric_names: Optional[List[str]] = None,
) -> ComparisonResponse:
    """Compare financial metrics across 2-5 documents and calculate YoY/QoQ deltas."""
    str_ids = [str(doc_id) for doc_id in document_ids]

    query = db.query(FinancialMetric).filter(
        FinancialMetric.document_id.in_(document_ids)
    )
    if metric_names:
        query = query.filter(FinancialMetric.metric_name.in_(metric_names))

    metrics = query.all()

    # Group values by metric_name -> {str(doc_id): value}
    grouped: dict[str, dict[str, float]] = {}
    for m in metrics:
        if m.value is None:
            continue
        if m.metric_name not in grouped:
            grouped[m.metric_name] = {}
        grouped[m.metric_name][str(m.document_id)] = m.value

    deltas: List[DeltaItem] = []
    for metric_name, values in grouped.items():
        doc_vals = [values.get(doc_id) for doc_id in str_ids if doc_id in values]
        if len(doc_vals) >= 2:
            first = doc_vals[0]
            last = doc_vals[-1]
            abs_delta = round(last - first, 4)
            pct_delta = round(((last - first) / abs(first) * 100.0), 2) if first != 0 else 0.0
        else:
            abs_delta = 0.0
            pct_delta = 0.0

        deltas.append(
            DeltaItem(
                metric_name=metric_name,
                values=values,
                absolute_delta=abs_delta,
                percent_delta=pct_delta,
            )
        )

    return ComparisonResponse(document_ids=document_ids, deltas=deltas)
