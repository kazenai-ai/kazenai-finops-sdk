"""Flask spend adapter tests."""

from __future__ import annotations

import pytest

flask = pytest.importorskip("flask")

from kazenai_finops.spend.adapters.flask import finops_after_request, finops_before_request


def test_flask_before_request_allows(finops_client):
    app = flask.Flask(__name__)
    app.before_request(finops_before_request(finops_client, org_id="o", run_id="r"))

    @app.get("/")
    def index():
        return {"ok": True}

    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200


def test_flask_before_request_blocks(mock_finops_state, finops_client):
    mock_finops_state["blocked"] = True
    app = flask.Flask(__name__)
    app.before_request(finops_before_request(finops_client, org_id="o", run_id="r"))

    @app.get("/")
    def index():
        return {"ok": True}

    resp = app.test_client().get("/")
    assert resp.status_code == 402


def test_flask_after_request_header(finops_client):
    app = flask.Flask(__name__)
    app.after_request(finops_after_request(finops_client, "org-a"))

    @app.get("/")
    def index():
        return {"ok": True}

    resp = app.test_client().get("/")
    assert resp.headers.get("X-Kazen-Spend-USD") is not None
