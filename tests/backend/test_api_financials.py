"""Financial endpoint tests."""
import pytest


@pytest.mark.integration
def test_metrics_empty(client, sample_pdf_bytes):
    files = {"file": ("m.pdf", sample_pdf_bytes, "application/pdf")}
    doc_id = client.post("/api/v1/documents/upload", files=files).json()["document_id"]

    resp = client.get(f"/api/v1/financial-metrics/{doc_id}")
    assert resp.status_code == 200
    assert resp.json()["metrics"] == []


@pytest.mark.integration
def test_health_score_default_zero(client, sample_pdf_bytes):
    files = {"file": ("h.pdf", sample_pdf_bytes, "application/pdf")}
    doc_id = client.post("/api/v1/documents/upload", files=files).json()["document_id"]

    resp = client.get(f"/api/v1/health-score/{doc_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_score"] == 0.0


@pytest.mark.integration
def test_compare_documents(client, sample_pdf_bytes):
    files1 = {"file": ("doc1.pdf", b"%PDF-1.4\n1", "application/pdf")}
    files2 = {"file": ("doc2.pdf", b"%PDF-1.4\n2", "application/pdf")}
    id1 = client.post("/api/v1/documents/upload", files=files1).json()["document_id"]
    id2 = client.post("/api/v1/documents/upload", files=files2).json()["document_id"]

    resp = client.post("/api/v1/financials/compare", json={"document_ids": [id1, id2]})
    if resp.status_code == 404:
        resp = client.post("/api/v1/compare", json={"document_ids": [id1, id2]})
    assert resp.status_code == 200
    assert "deltas" in resp.json()