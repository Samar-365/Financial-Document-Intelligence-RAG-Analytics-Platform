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

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Query, UploadFile, status

PDF_MAGIC = b"%PDF"


def _run_pipeline_task(doc_id: UUID, content: bytes):
    from app.db.session import SessionLocal
    from app.services.document_service import process_document_pipeline
    bg_db = SessionLocal()
    try:
        process_document_pipeline(bg_db, doc_id, file_bytes=content)
    except Exception:
        pass
    finally:
        bg_db.close()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    company_name: Optional[str] = Form(None),
    fiscal_year: Optional[int] = Form(None),
    fiscal_period: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
) -> DocumentUploadResponse:
    content = await file.read()

    from app.core.security import validate_document_upload
    try:
        validate_document_upload(content, file.filename or "file.pdf")
    except Exception as e:
        raise InvalidFileException(str(e))

    file_hash = sha256_bytes(content)
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing:
        if existing.status == "FAILED":
            db.delete(existing)
            db.commit()
        else:
            raise DuplicateDocumentException(file_hash)

    doc = Document(
        user_id=user_id,
        filename=file.filename or "unnamed.pdf",
        file_hash=file_hash,
        file_size_bytes=len(content),
        company_name=company_name,
        fiscal_year=fiscal_year,
        fiscal_period=fiscal_period,
        status="UPLOADED",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Queue ingestion pipeline in background
    background_tasks.add_task(_run_pipeline_task, doc.id, content)

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