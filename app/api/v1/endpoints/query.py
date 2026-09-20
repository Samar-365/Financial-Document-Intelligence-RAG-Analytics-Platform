"""Endpoint #5: RAG query."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.errors import DocumentNotFoundException
from app.models.document import Document
from app.schemas.query import QueryRequest, RAGResponse

# Import from Dev 1 when real implementation lands in Sprint 2.
# from app.rag.retriever import RAGService  # noqa: F401
from app.services.rag_service import RAGService

router = APIRouter(tags=["query"])


@router.post("/query", response_model=RAGResponse)
async def query_document(
    payload: QueryRequest,
    db: Session = Depends(get_db),
) -> RAGResponse:
    doc = db.query(Document).filter(Document.id == payload.document_id).first()
    if not doc:
        raise DocumentNotFoundException(str(payload.document_id))

    rag_service = RAGService(db)
    return rag_service.query(
        document_id=payload.document_id,
        question=payload.question,
        top_k=payload.top_k,
    )