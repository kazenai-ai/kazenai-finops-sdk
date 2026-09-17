"""FinOps Agent spend API client (budget check + org spend reports)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class BudgetCheckResult:
    allowed: bool
    reason: str = ""
    projected_spend_usd: Optional[float] = None
    budget_usd: Optional[float] = None
    raw: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class OrgSpendSummary:
    org_id: str
    total_cost_usd: float
    event_count: int = 0
    avoided_cost_usd: float = 0.0
    raw: Optional[Dict[str, Any]] = None


class FinOpsSpendClient:
    """Thin HTTP client for KazenAI Agent FinOps spend endpoints."""

    def __init__(self, base_url: str, api_key: str = "", *, timeout_s: float = 5.0) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.api_key = str(api_key or "")
        self.timeout_s = float(timeout_s)

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if not self.api_key:
            return headers
        if self.api_key.count(".") == 2:
            headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            headers["X-API-Key"] = self.api_key
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.base_url:
            raise ValueError("FinOps base_url is required")
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=self._headers(),
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read().decode("utf-8") or "{}"
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8") or "{}"
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"detail": raw}
            if exc.code == 402:
                return parsed
            raise

    def get_org_spend(self, org_id: str, *, period_days: int = 30) -> OrgSpendSummary:
        qs = f"?period_days={int(period_days)}" if period_days else ""
        payload = self._request("GET", f"/v1/org/{org_id}/spend{qs}")
        return OrgSpendSummary(
            org_id=org_id,
            total_cost_usd=float(payload.get("total_cost_usd") or payload.get("cost_usd") or 0.0),
            event_count=int(payload.get("event_count") or 0),
            avoided_cost_usd=float(payload.get("avoided_cost_usd") or 0.0),
            raw=payload,
        )

    def check_budget(
        self,
        *,
        org_id: str,
        run_id: str,
        projected_spend_usd: Optional[float] = None,
        workspace_id: str = "default",
        model: Optional[str] = None,
        input_tokens: Optional[int] = None,
        max_tokens: Optional[int] = None,
        reserve: bool = True,
        increment_step: bool = True,
    ) -> BudgetCheckResult:
        body: Dict[str, Any] = {
            "org_id": org_id,
            "workspace_id": workspace_id,
            "run_id": run_id,
            "reserve": reserve,
            "increment_step": increment_step,
        }
        if projected_spend_usd is not None:
            body["projected_spend_usd"] = float(projected_spend_usd)
        if model:
            body["model"] = model
        if input_tokens is not None:
            body["input_tokens"] = int(input_tokens)
        if max_tokens is not None:
            body["max_tokens"] = int(max_tokens)
        payload = self._request("POST", "/v1/budget/check", body=body)
        if isinstance(payload.get("detail"), dict):
            detail = payload["detail"]
            return BudgetCheckResult(
                allowed=False,
                reason=str(detail.get("reason") or ""),
                projected_spend_usd=detail.get("projected_spend_usd"),
                budget_usd=detail.get("budget_usd"),
                raw=detail,
            )
        allowed = bool(payload.get("allowed", True))
        return BudgetCheckResult(
            allowed=allowed,
            reason=str(payload.get("reason") or payload.get("detail") or ""),
            projected_spend_usd=payload.get("projected_spend_usd"),
            budget_usd=payload.get("budget_usd"),
            raw=payload,
        )

    def reconcile_budget(
        self,
        *,
        org_id: str,
        run_id: str,
        reserved_cost_usd: float,
        actual_cost_usd: float,
        workspace_id: str = "default",
    ) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/v1/budget/reconcile",
            body={
                "org_id": org_id,
                "workspace_id": workspace_id,
                "run_id": run_id,
                "reserved_cost_usd": float(reserved_cost_usd),
                "actual_cost_usd": float(actual_cost_usd),
            },
        )


    def reserve_lifecycle(
        self,
        *,
        org_id: str,
        workspace_id: str,
        call_id: str,
        estimated_usd_micros: int,
        attempt: int = 1,
        idempotency_key: str = "",
        run_id: str = "",
        feature: str = "",
    ) -> Dict[str, Any]:
        """FINAL_1 P2-6 — versioned PG admission (reservation.lifecycle.v1)."""
        body: Dict[str, Any] = {
            "lifecycle_version": "reservation.lifecycle.v1",
            "call_id": call_id,
            "attempt": max(1, int(attempt)),
            "idempotency_key": idempotency_key or f"sdk:reserve:{call_id}:{attempt}",
            "org_id": org_id,
            "workspace_id": workspace_id,
            "estimated_usd_micros": int(estimated_usd_micros),
            "run_id": run_id or "",
        }
        if feature:
            body["feature"] = feature
        return self._request("POST", "/v1/budget/reserve", body=body)

    def settle_lifecycle(
        self,
        *,
        org_id: str,
        reservation_id: str,
        call_id: str,
        event: str,
        attempt: int = 1,
        idempotency_key: str = "",
        actual_usd_micros: Optional[int] = None,
    ) -> Dict[str, Any]:
        """FINAL_1 P2-6 — versioned PG settlement (reservation.lifecycle.v1)."""
        body: Dict[str, Any] = {
            "lifecycle_version": "reservation.lifecycle.v1",
            "reservation_id": reservation_id,
            "call_id": call_id,
            "attempt": max(1, int(attempt)),
            "idempotency_key": idempotency_key or f"sdk:settle:{reservation_id}:{event}",
            "event": event,
            "org_id": org_id,
        }
        if actual_usd_micros is not None:
            body["actual_usd_micros"] = int(actual_usd_micros)
        return self._request("POST", "/v1/budget/settle", body=body)
