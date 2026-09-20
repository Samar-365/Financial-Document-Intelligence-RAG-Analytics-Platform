"""API tests for document endpoints."""
import pytest


@pytest.mark.integration
def test_upload_valid_pdf(client, sample_pdf_bytes):
    files = {"file": ("test.pdf", sample_pdf_bytes, "application/pdf")}
    resp = client.post("/api/v1/documents/upload", files=files)
    assert resp.status_code == 201
    body = resp.json()
    assert body["filename"] == "test.pdf"
    assert body["status"] == "UPLOADED"


@pytest.mark.integration
def test_upload_rejects_non_pdf(client):
    files = {"file": ("evil.txt", b"not a pdf", "text/plain")}
    resp = client.post("/api/v1/documents/upload", files=files)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "DOC_001"


@pytest.mark.integration
def test_upload_rejects_duplicate(client, sample_pdf_bytes):
    files = {"file": ("a.pdf", sample_pdf_bytes, "application/pdf")}
    client.post("/api/v1/documents/upload", files=files)
    resp = client.post("/api/v1/documents/upload", files=files)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "DOC_002"


@pytest.mark.integration
def test_list_documents_empty(client):
    resp = client.get("/api/v1/documents")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []


@pytest.mark.integration
def test_get_missing_document(client):
    fake_id = "11111111-1111-1111-1111-111111111111"
    resp = client.get(f"/api/v1/documents/{fake_id}")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "DOC_003"


@pytest.mark.integration
def test_delete_document(client, sample_pdf_bytes):
    files = {"file": ("del.pdf", sample_pdf_bytes, "application/pdf")}
    created = client.post("/api/v1/documents/upload", files=files).json()
    doc_id = created["document_id"]

    resp = client.delete(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 404