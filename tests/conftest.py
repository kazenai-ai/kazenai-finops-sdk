"""Shared fixtures including mock FinOps HTTP server."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

CORE_ROOT = Path(__file__).resolve().parents[2] / "kazenai-core"
if CORE_ROOT.is_dir() and str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from kazenai_finops.spend.client import FinOpsSpendClient


@pytest.fixture
def mock_finops_state():
    return {"blocked": False, "spend_usd": 2.5, "event_count": 12}


@pytest.fixture
def mock_finops_app(mock_finops_state):
    app = FastAPI()

    @app.get("/v1/org/{org_id}/spend")
    def org_spend(org_id: str, period_days: int = 0):
        return {
            "org_id": org_id,
            "total_cost_usd": mock_finops_state["spend_usd"],
            "event_count": mock_finops_state["event_count"],
            "avoided_cost_usd": 0.25,
            "period_days": period_days or None,
        }

    @app.post("/v1/budget/check")
    def budget_check(body: dict):
        if mock_finops_state["blocked"]:
            return {"allowed": False, "reason": "over_budget", "budget_usd": 1.0}
        return {
            "allowed": True,
            "reason": "",
            "projected_spend_usd": body.get("projected_spend_usd"),
            "budget_usd": 10.0,
        }

    @app.post("/v1/events")
    def ingest_events(body: dict):
        return {"accepted": len(body.get("events") or [])}

    return app


@pytest.fixture
def mock_finops_url(mock_finops_app):
    with TestClient(mock_finops_app) as client:
        yield client


@pytest.fixture
def finops_client(mock_finops_url):
    transport = mock_finops_url
    base_url = str(transport.base_url).rstrip("/")

    class _BoundClient(FinOpsSpendClient):
        def _request(self, method, path, *, body=None):
            if method == "GET":
                resp = transport.get(path)
            else:
                resp = transport.post(path, json=body or {})
            return resp.json()

    return _BoundClient(base_url, api_key="test-key")
