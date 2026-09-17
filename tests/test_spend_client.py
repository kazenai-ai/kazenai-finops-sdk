"""FinOpsSpendClient tests against mock server."""

from __future__ import annotations

import pytest

from kazenai_finops.spend.client import FinOpsSpendClient


def test_get_org_spend(finops_client):
    summary = finops_client.get_org_spend("org-a", period_days=7)
    assert summary.org_id == "org-a"
    assert summary.total_cost_usd == pytest.approx(2.5)
    assert summary.event_count == 12


def test_check_budget_allowed(finops_client):
    result = finops_client.check_budget(org_id="org-a", run_id="r1", projected_spend_usd=0.5)
    assert result.allowed is True
    assert result.budget_usd == 10.0


def test_check_budget_blocked(finops_client, mock_finops_state):
    mock_finops_state["blocked"] = True
    result = finops_client.check_budget(org_id="org-a", run_id="r1", projected_spend_usd=5.0)
    assert result.allowed is False
    assert "over_budget" in result.reason


def test_client_requires_base_url():
    client = FinOpsSpendClient("")
    with pytest.raises(ValueError, match="base_url"):
        client.get_org_spend("org")


def test_api_key_bearer_header():
    client = FinOpsSpendClient("http://localhost:8090", "eyJhbGci.test.sig")
    headers = client._headers()
    assert headers["Authorization"].startswith("Bearer ")


def test_api_key_header_for_plain_key():
    client = FinOpsSpendClient("http://localhost:8090", "plain-key")
    headers = client._headers()
    assert headers["X-API-Key"] == "plain-key"
