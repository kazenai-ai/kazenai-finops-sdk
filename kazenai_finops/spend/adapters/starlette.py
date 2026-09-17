"""Starlette middleware for FinOps spend reporting."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from kazenai_finops.spend.client import FinOpsSpendClient


class FinOpsSpendMiddleware(BaseHTTPMiddleware):
    """Adds org spend summary header and optional pre-request budget gate."""

    def __init__(
        self,
        app,
        *,
        client: FinOpsSpendClient,
        org_id: str,
        run_id: str = "http",
        projected_spend_usd: float = 0.0,
        enforce_budget: bool = False,
    ) -> None:
        super().__init__(app)
        self._client = client
        self._org_id = org_id
        self._run_id = run_id
        self._projected = projected_spend_usd
        self._enforce = enforce_budget

    async def dispatch(self, request: Request, call_next) -> Response:
        if self._enforce:
            result = self._client.check_budget(
                org_id=self._org_id,
                run_id=self._run_id,
                projected_spend_usd=self._projected,
            )
            if not result.allowed:
                from starlette.responses import JSONResponse

                return JSONResponse(
                    status_code=402,
                    content={"detail": result.reason or "budget exceeded"},
                )
        response = await call_next(request)
        try:
            summary = self._client.get_org_spend(self._org_id)
            response.headers["X-Kazen-Spend-USD"] = f"{summary.total_cost_usd:.6f}"
        except Exception:
            pass
        return response
