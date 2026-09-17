"""Error envelope tests."""
import pytest


@pytest.mark.integration
def test_validation_error_envelope(client):
    # Missing required field
    resp = client.post("/api/v1/query", json={})
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "VALIDATION_001"


@pytest.mark.integration
def test_health_endpoint(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["status"] in {"ok", "degraded"}