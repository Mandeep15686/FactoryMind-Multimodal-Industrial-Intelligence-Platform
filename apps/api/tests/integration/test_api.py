"""Integration tests over the FastAPI app (TestClient, dev auth)."""
from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_trigger_inspection():
    r = client.post("/api/v1/inspections", json={"machine_id": "M12", "triggered_by": "MANUAL"})
    assert r.status_code == 200
    body = r.json()
    assert body["machine_id"] == "M12"
    assert "jira_ticket_id" in body


def test_knowledge_query():
    r = client.post("/api/v1/knowledge/query", json={"query": "bearing wear", "top_k": 3})
    assert r.status_code == 200
    assert "documents" in r.json()


def test_dashboard_overview():
    r = client.get("/api/v1/dashboard/overview")
    assert r.status_code == 200
    assert "machines_total" in r.json()
