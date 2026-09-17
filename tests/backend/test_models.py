"""Tests for SQLAlchemy models and cascades (D2-M2)."""
import pytest

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User


@pytest.mark.unit
def test_create_user_and_document(db_session):
    user = User(email="alice@test.com", full_name="Alice")
    db_session.add(user)
    db_session.flush()

    doc = Document(user_id=user.id, filename="report.pdf", file_hash="abc123")
    db_session.add(doc)
    db_session.flush()

    assert doc.id is not None
    assert doc.owner.email == "alice@test.com"


@pytest.mark.unit
def test_cascade_delete_document_removes_chunks(db_session):
    user = User(email="bob@test.com")
    db_session.add(user)
    db_session.flush()

    doc = Document(user_id=user.id, filename="q1.pdf", file_hash="hash1")
    db_session.add(doc)
    db_session.flush()

    chunk = DocumentChunk(
        document_id=doc.id, chunk_index=0, content="hello", page_number=1
    )
    db_session.add(chunk)
    db_session.flush()

    doc_id = doc.id
    db_session.delete(doc)
    db_session.flush()

    remaining = (
        db_session.query(DocumentChunk)
        .filter(DocumentChunk.document_id == doc_id)
        .all()
    )
    assert remaining == []


@pytest.mark.unit
def test_duplicate_file_hash_raises(db_session):
    from sqlalchemy.exc import IntegrityError

    user = User(email="dup@test.com")
    db_session.add(user)
    db_session.flush()

    db_session.add(Document(user_id=user.id, filename="a.pdf", file_hash="same"))
    db_session.flush()

    db_session.add(Document(user_id=user.id, filename="b.pdf", file_hash="same"))
    with pytest.raises(IntegrityError):
        db_session.flush()