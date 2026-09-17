from typing import Optional

from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db: Session):
        super().__init__(Document, db)

    def find_by_hash(self, file_hash: str) -> Optional[Document]:
        return (
            self.db.query(Document)
            .filter(Document.file_hash == file_hash)
            .first()
        )