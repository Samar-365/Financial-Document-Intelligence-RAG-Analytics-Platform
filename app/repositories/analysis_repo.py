from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.analysis_result import AnalysisResult
from app.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository[AnalysisResult]):
    def __init__(self, db: Session):
        super().__init__(AnalysisResult, db)

    def find_by_document(self, document_id: UUID) -> Optional[AnalysisResult]:
        return (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.document_id == document_id)
            .first()
        )