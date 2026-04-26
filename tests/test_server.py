"""FastAPI integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from agenthound.server import create_app


def test_health() -> None:
    client = TestClient(create_app())
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_scan_sample_returns_valid_payload() -> None:
    client = TestClient(create_app())
    res = client.get("/api/scan/sample")
    assert res.status_code == 200
    body = res.json()
    assert body["schema_version"] == "1"
    assert body["summary"]["total_paths"] > 0
    assert body["graph"]["nodes"]
    assert body["graph"]["edges"]


def test_samples_endpoint_returns_both_files() -> None:
    client = TestClient(create_app())
    res = client.get("/api/samples")
    assert res.status_code == 200
    body = res.json()
    assert "claude_desktop_config" in body
    assert "tool_catalog" in body
