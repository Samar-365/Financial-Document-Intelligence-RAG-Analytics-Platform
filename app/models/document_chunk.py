"""SQLAlchemy ORM model for persistent vector-indexed document chunks (Module 10.1).

Maps the `document_chunks` table with pgvector Vector(384) column and HNSW cosine index
for sub-50ms nearest-neighbor retrieval across 50,000+ embeddings.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Index,
    Uuid,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, JSON

class SafeVector(TypeDecorator):
    """Database-agnostic vector type decorator: uses pgvector on PostgreSQL and JSON elsewhere."""
    impl = JSON
    cache_ok = True

    def __init__(self, dim: int = 384):
        self.dim = dim
        super().__init__()

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from pgvector.sqlalchemy import Vector
                return dialect.type_descriptor(Vector(self.dim))
            except ImportError:
                from sqlalchemy.dialects.postgresql import ARRAY
                from sqlalchemy import Float
                return dialect.type_descriptor(ARRAY(Float))
        return dialect.type_descriptor(JSON())


from app.db.base import Base


class DocumentChunk(Base): #ORM model representing a single document chunk with its 384-dim embedding vector
    """Persistent document chunk with pgvector embedding for cosine similarity search.

    Columns:
        id: Primary key UUID for the chunk row.
        document_id: Identifier of the parent document.
        chunk_id: Original UUIDv4 from TextChunkDTO (unique).
        chunk_index: 0-based sequential position within the document.
        page_number: 1-based originating PDF page.
        content: Full text content of the chunk.
        token_estimate: Estimated token count (4-char heuristic).
        is_table_chunk: Whether chunk contains tabular markdown.
        embedding: 384-dimensional dense vector (pgvector Vector type).
        created_at: Timestamp of row insertion.
    """

    __tablename__ = "document_chunks"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_id = Column( #Original chunk UUID from TextChunkDTO — unique across all documents
        String(36),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    chunk_index = Column( #Sequential position of chunk within document (0-based)
        Integer,
        nullable=False,
    )
    page_number = Column( #Originating PDF page number (1-based)
        Integer,
        nullable=False,
    )
    content = Column( #Full text content of the chunk including preserved markdown structures
        Text,
        nullable=False,
    )
    token_estimate = Column( #Estimated token count using the 4-characters-per-token heuristic
        Integer,
        nullable=False,
        default=0,
    )
    is_table_chunk = Column( #Flag indicating whether chunk contains tabular markdown structures
        Boolean,
        nullable=False,
        default=False,
    )
    embedding = Column( #384-dimensional dense vector stored via pgvector extension
        SafeVector(384),
        nullable=False,
    )
    created_at = Column( #UTC timestamp of when this chunk was persisted
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return (
            f"<DocumentChunk(id={self.id!r}, document_id={self.document_id!r}, "
            f"chunk_index={self.chunk_index}, page={self.page_number})>"
        )
