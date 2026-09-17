"""Endpoints #1–#4: document CRUD."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_id, get_db
from app.core.config import settings
from app.core.errors import (
    DocumentNotFoundException,
    DuplicateDocumentException,
    InvalidFileException,
)
from app.models.document import Document
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.utils.hashing import sha256_bytes

router = APIRouter(prefix="/documents", tags=["documents"])

PDF_MAGIC = b"%PDF"


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> DocumentUploadResponse:
    content = await file.read()

    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise InvalidFileException(
            f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit"
        )
    if not content.startswith(PDF_MAGIC):
        raise InvalidFileException("Uploaded file is not a valid PDF")

    file_hash = sha256_bytes(content)
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing:
        raise DuplicateDocumentException(file_hash)

    doc = Document(
        user_id=user_id,
        filename=file.filename or "unnamed.pdf",
        file_hash=file_hash,
        file_size_bytes=len(content),
        status="UPLOADED",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return DocumentUploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        status=doc.status,
        message="Document uploaded and queued for processing",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> DocumentListResponse:
    query = db.query(Document).filter(Document.user_id == user_id)
    if status_filter:
        query = query.filter(Document.status == status_filter)

    total = query.count()
    items = (
        query.order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> DocumentResponse:
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user_id)
        .first()
    )
    if not doc:
        raise DocumentNotFoundException(str(document_id))
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> None:
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user_id)
        .first()
    )
    if not doc:
        raise DocumentNotFoundException(str(document_id))
    db.delete(doc)
    db.commit()