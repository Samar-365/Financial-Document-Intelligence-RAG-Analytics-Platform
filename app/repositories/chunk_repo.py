from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.repositories.base import BaseRepository


class ChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self, db: Session):
        super().__init__(DocumentChunk, db)

    def list_for_document(self, document_id: UUID) -> List[DocumentChunk]:
        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )