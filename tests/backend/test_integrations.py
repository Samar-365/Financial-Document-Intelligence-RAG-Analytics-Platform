"""End-to-end smoke test."""
import pytest


@pytest.mark.integration
@pytest.mark.smoke
def test_full_loop(client, sample_pdf_bytes):
    # 1. Upload
    files = {"file": ("e2e.pdf", sample_pdf_bytes, "application/pdf")}
    upload = client.post("/api/v1/documents/upload", files=files)
    assert upload.status_code == 201
    doc_id = upload.json()["document_id"]

    # 2. List
    listing = client.get("/api/v1/documents").json()
    assert listing["total"] == 1

    # 3. Query
    q = client.post(
        "/api/v1/query",
        json={"document_id": doc_id, "question": "Summarize."},
    )
    assert q.status_code == 200

    # 4. Metrics
    m = client.get(f"/api/v1/financial-metrics/{doc_id}")
    assert m.status_code == 200

    # 5. Delete
    d = client.delete(f"/api/v1/documents/{doc_id}")
    assert d.status_code == 204