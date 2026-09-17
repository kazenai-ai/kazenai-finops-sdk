"""Extended FinOpsSpendClient tests."""

from __future__ import annotations

import json
import urllib.error

import pytest

from kazenai_finops.spend.client import BudgetCheckResult, FinOpsSpendClient, OrgSpendSummary


def test_org_spend_summary_dataclass():
    s = OrgSpendSummary(org_id="o", total_cost_usd=1.0, event_count=3, raw={"x": 1})
    assert s.org_id == "o"


def test_budget_check_result_dataclass():
    r = BudgetCheckResult(allowed=False, reason="cap", budget_usd=5.0)
    assert r.allowed is False


def test_mock_finops_events_ingest(mock_finops_url):
    resp = mock_finops_url.post("/v1/events", json={"events": [{"event_type": "model.call"}]})
    assert resp.status_code == 200
    assert resp.json()["accepted"] == 1


def test_check_budget_402_response_parsed(finops_client, mock_finops_state):
    mock_finops_state["blocked"] = True
    result = finops_client.check_budget(org_id="o", run_id="r", projected_spend_usd=99.0)
    assert isinstance(result, BudgetCheckResult)


def test_get_org_spend_zero_period(finops_client):
    summary = finops_client.get_org_spend("org-z", period_days=0)
    assert summary.total_cost_usd >= 0
