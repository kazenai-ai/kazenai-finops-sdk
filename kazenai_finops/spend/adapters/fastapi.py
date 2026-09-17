"""FastAPI dependency for FinOps budget checks."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from kazenai_finops.spend.client import FinOpsSpendClient


def require_finops_budget(
    client: FinOpsSpendClient,
    *,
    org_id: str,
    run_id: str,
    projected_spend_usd: float = 0.0,
    workspace_id: str = "default",
) -> Callable[..., Dict[str, Any]]:
    """Return a FastAPI dependency that blocks with 402 when budget is exceeded."""

    def _dep() -> Dict[str, Any]:
        result = client.check_budget(
            org_id=org_id,
            run_id=run_id,
            projected_spend_usd=projected_spend_usd,
            workspace_id=workspace_id,
        )
        if not result.allowed:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=402,
                detail={
                    "reason": result.reason,
                    "projected_spend_usd": result.projected_spend_usd,
                    "budget_usd": result.budget_usd,
                },
            )
        return {
            "allowed": result.allowed,
            "reason": result.reason,
            "projected_spend_usd": result.projected_spend_usd,
            "budget_usd": result.budget_usd,
        }

    return _dep


def attach_spend_header_middleware(app: Any, client: FinOpsSpendClient, org_id: str) -> None:
    """Attach middleware that adds X-Kazen-Spend-USD on each response."""

    @app.middleware("http")
    async def _finops_spend_header(request, call_next):
        response = await call_next(request)
        try:
            summary = client.get_org_spend(org_id, period_days=30)
            response.headers["X-Kazen-Spend-USD"] = f"{summary.total_cost_usd:.6f}"
        except Exception:
            pass
        return response
