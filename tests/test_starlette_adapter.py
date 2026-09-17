"""Starlette spend middleware tests."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from kazenai_finops.spend.adapters.starlette import FinOpsSpendMiddleware


def test_starlette_middleware_adds_header(finops_client):
    app = FastAPI()
    app.add_middleware(FinOpsSpendMiddleware, client=finops_client, org_id="org-a")

    @app.get("/x")
    def x():
        return {"ok": True}

    resp = TestClient(app).get("/x")
    assert resp.status_code == 200
    assert "X-Kazen-Spend-USD" in resp.headers


def test_starlette_middleware_enforces_budget(mock_finops_state, finops_client):
    mock_finops_state["blocked"] = True
    app = FastAPI()
    app.add_middleware(
        FinOpsSpendMiddleware,
        client=finops_client,
        org_id="org-a",
        enforce_budget=True,
    )

    @app.get("/x")
    def x():
        return {"ok": True}

    resp = TestClient(app).get("/x")
    assert resp.status_code == 402
