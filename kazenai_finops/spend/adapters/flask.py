"""Flask hooks for FinOps spend guards."""

from __future__ import annotations

from typing import Any, Callable, Optional

from flask import g, request

from kazenai_finops.spend.client import FinOpsSpendClient


def finops_before_request(
    client: FinOpsSpendClient,
    *,
    org_id: str,
    run_id: str,
    projected_spend_usd: float = 0.0,
) -> Callable[[], Optional[Any]]:
    """Return a Flask before_request handler that enforces budget."""

    def _guard() -> Optional[Any]:
        result = client.check_budget(
            org_id=org_id,
            run_id=run_id,
            projected_spend_usd=projected_spend_usd,
        )
        g.finops_budget = result
        if not result.allowed:
            from flask import jsonify

            return jsonify({"detail": result.reason or "budget exceeded"}), 402
        return None

    return _guard


def finops_after_request(client: FinOpsSpendClient, org_id: str) -> Callable[[Any], Any]:
    """Return after_request hook that stamps spend header."""

    def _stamp(response):
        try:
            summary = client.get_org_spend(org_id)
            response.headers["X-Kazen-Spend-USD"] = f"{summary.total_cost_usd:.6f}"
        except Exception:
            pass
        return response

    return _stamp
