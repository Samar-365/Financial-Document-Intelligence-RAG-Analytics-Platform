from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.financial_metric import FinancialMetric
from app.repositories.base import BaseRepository


class MetricRepository(BaseRepository[FinancialMetric]):
    def __init__(self, db: Session):
        super().__init__(FinancialMetric, db)

    def list_for_document(self, document_id: UUID) -> List[FinancialMetric]:
        return (
            self.db.query(FinancialMetric)
            .filter(FinancialMetric.document_id == document_id)
            .all()
        )