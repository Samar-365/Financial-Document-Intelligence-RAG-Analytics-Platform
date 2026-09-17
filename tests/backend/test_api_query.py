"""Query endpoint tests."""
import pytest


@pytest.mark.integration
def test_query_missing_document(client):
    payload = {
        "document_id": "11111111-1111-1111-1111-111111111111",
        "question": "What is revenue?",
    }
    resp = client.post("/api/v1/query", json=payload)
    assert resp.status_code == 404


@pytest.mark.integration
def test_query_returns_stub_answer(client, sample_pdf_bytes):
    files = {"file": ("q.pdf", sample_pdf_bytes, "application/pdf")}
    doc_id = client.post("/api/v1/documents/upload", files=files).json()["document_id"]

    payload = {"document_id": doc_id, "question": "What is revenue?"}
    resp = client.post("/api/v1/query", json=payload)
    assert resp.status_code == 200
    assert "answer" in resp.json()