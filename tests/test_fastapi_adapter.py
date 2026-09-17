"""FastAPI spend adapter tests."""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from kazenai_finops.spend.adapters.fastapi import attach_spend_header_middleware, require_finops_budget


def test_require_finops_budget_allows(finops_client):
    app = FastAPI()

    @app.get("/run")
    def run(budget=Depends(require_finops_budget(finops_client, org_id="o", run_id="r"))):
        return budget

    client = TestClient(app)
    resp = client.get("/run")
    assert resp.status_code == 200
    assert resp.json()["allowed"] is True


def test_require_finops_budget_blocks(mock_finops_state, finops_client):
    mock_finops_state["blocked"] = True
    app = FastAPI()

    @app.get("/run")
    def run(budget=Depends(require_finops_budget(finops_client, org_id="o", run_id="r", projected_spend_usd=9))):
        return budget

    client = TestClient(app)
    resp = client.get("/run")
    assert resp.status_code == 402


def test_spend_header_middleware(finops_client, mock_finops_app):
    app = FastAPI()

    @app.get("/ok")
    def ok():
        return {"ok": True}

    attach_spend_header_middleware(app, finops_client, "org-a")
    client = TestClient(app)
    resp = client.get("/ok")
    assert resp.status_code == 200
    assert "X-Kazen-Spend-USD" in resp.headers
