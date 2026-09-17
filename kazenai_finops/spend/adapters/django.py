"""Django middleware for FinOps spend guards."""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse, JsonResponse

from kazenai_finops.spend.client import FinOpsSpendClient


class FinOpsSpendMiddleware:
    """Django middleware: optional budget gate + spend summary response header."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response
        base = __import__("os").environ.get("KAZENAI_FINOPS_URL", "").strip()
        key = __import__("os").environ.get("KAZENAI_FINOPS_API_KEY", "").strip()
        self._client = FinOpsSpendClient(base, key)
        self._org_id = __import__("os").environ.get("KAZENAI_FINOPS_ORG_ID", "local")
        self._run_id = __import__("os").environ.get("KAZENAI_FINOPS_RUN_ID", "django")
        self._projected = float(__import__("os").environ.get("KAZENAI_FINOPS_PROJECTED_USD", "0"))
        self._enforce = __import__("os").environ.get("KAZENAI_FINOPS_ENFORCE_BUDGET", "0") in {"1", "true"}

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self._enforce and self._client.base_url:
            result = self._client.check_budget(
                org_id=self._org_id,
                run_id=self._run_id,
                projected_spend_usd=self._projected,
            )
            if not result.allowed:
                return JsonResponse({"detail": result.reason or "budget exceeded"}, status=402)
        response = self.get_response(request)
        if self._client.base_url:
            try:
                summary = self._client.get_org_spend(self._org_id)
                response["X-Kazen-Spend-USD"] = f"{summary.total_cost_usd:.6f}"
            except Exception:
                pass
        return response
