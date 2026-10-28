"""Legacy budget endpoints under Control.

Hosted Agent FinOps runs the Control lifecycle and answers the legacy
``/v1/budget/check`` and ``/v1/budget/reconcile`` with 501 ``unsupported_mode``.
The client says so plainly instead of surfacing a bare HTTPError, and both
methods are deprecated in favour of ``kazenai.monitor`` reserve/settle.
"""

from __future__ import annotations

import io
import json
import urllib.error

import pytest

from kazenai_finops.spend import client as client_mod
from kazenai_finops.spend.client import FinOpsSpendClient, LegacyBudgetEndpointUnsupported


def _unsupported(url: str) -> urllib.error.HTTPError:
    body = json.dumps(
        {
            "detail": {
                "error_code": "unsupported_mode",
                "reason": "POST /v1/budget/check is unsupported under Control; use POST /v1/budget/reserve",
            }
        }
    ).encode("utf-8")
    return urllib.error.HTTPError(url, 501, "Not Implemented", {}, io.BytesIO(body))


def test_check_budget_is_deprecated(finops_client):
    with pytest.warns(DeprecationWarning, match="kazenai.monitor"):
        finops_client.check_budget(org_id="org-a", run_id="r1", projected_spend_usd=0.5)


def test_reconcile_budget_is_deprecated(monkeypatch):
    client = FinOpsSpendClient("https://finops.example.test", "plain-key")
    monkeypatch.setattr(client, "_request", lambda *a, **k: {"ok": True})
    with pytest.warns(DeprecationWarning, match="kazenai.monitor"):
        client.reconcile_budget(org_id="org-a", run_id="r1", reserved_cost_usd=0.1, actual_cost_usd=0.1)


@pytest.mark.parametrize("method", ["check_budget", "reconcile_budget"])
def test_control_refusal_raises_a_named_error(monkeypatch, method):
    def _urlopen(req, timeout=None):
        raise _unsupported(req.full_url)

    monkeypatch.setattr(client_mod.urllib.request, "urlopen", _urlopen)
    client = FinOpsSpendClient("https://finops.example.test", "plain-key")
    kwargs = {"org_id": "org-a", "run_id": "r1"}
    if method == "reconcile_budget":
        kwargs.update(reserved_cost_usd=0.1, actual_cost_usd=0.1)
    with pytest.warns(DeprecationWarning):
        with pytest.raises(LegacyBudgetEndpointUnsupported, match="kazenai.monitor"):
            getattr(client, method)(**kwargs)
