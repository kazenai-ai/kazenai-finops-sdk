"""kazenai-finops — customer-facing SDK for the KazenAI reliability platform.

This package is a thin re-export wrapper around ``kazenai-core``. All the
heavy lifting (event schema, enforcement, loop detection, sinks) lives in
``kazenai-core``. The wrapper exists so:

    * Customer-facing PyPI name matches the v3 strategic plan
      ("pip install kazenai-finops").
    * Framework adapters can be installed via extras
      (``pip install kazenai-finops[langchain]``).
    * Future SDK-level features that don't belong in the engine (e.g.
      hosted-backend convenience helpers, onboarding wizards) land here.

Public API:
    monitor(...)              — wrap OpenAI Chat Completions and Responses / Anthropic Messages (sync and async)
    BudgetExceeded            — hard local/shared budget deny (before provider)
    SharedBudget              — one local cap shared by several monitor() clients
    BudgetUnavailable         — no usable answer from Agent FinOps (unreachable, timed out, or an error status) under fail-closed
    InvalidAttribution        — Agent FinOps refused the call's customer or feature ID (a BudgetUnavailable)
    KazenCircuitBreaker       — soft trajectory pause (after a completed call)
    KazenBudgetExceeded       — deprecated alias of KazenCircuitBreaker (not hard BudgetExceeded)
    KazenEvent                — canonical event schema (re-export)
    FinOpsController          — lower-level controller for power users
    use_attribution           — name the customer (and feature/workflow) for calls in a block
    AttributionConflict       — two different customer IDs named for one call
    AttributionContext        — the attribution in force for the current call
    CustomerIdRequired        — monitor(require_customer_id=True) refused a call with no customer ID
    LoopDetected              — monitor(loop_guard="block") refused a call that repeats like a loop
"""

from __future__ import annotations

# Re-export the core public API. Customers import from kazenai_finops; the
# engine lives in kazenai-core. If a user upgrades only kazenai-core they
# still get the new behaviour through this re-export.
from kazenai import (
    AttributionConflict,
    AttributionContext,
    BudgetExceeded,
    BudgetUnavailable,
    CustomerIdRequired,
    FinOpsConfig,
    FinOpsController,
    InvalidAttribution,
    KazenCircuitBreaker,
    KazenEvent,
    LoopDetected,
    SharedBudget,
    StreamCutoffError,
    UnknownModelError,
    monitor,
    use_attribution,
)
from kazenai.schema import new_id, now_ms
from kazenai.spine import aguarded_llm_call, guarded_embedding_call, guarded_llm_call

# Deprecated alias: soft circuit-breaker only. Hard caps raise BudgetExceeded.
KazenBudgetExceeded = KazenCircuitBreaker

# Prefer the installed distribution version. Fallback is only for editable /
# source checkouts where package metadata is unavailable.
try:
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version as _pkg_version

    __version__ = _pkg_version("kazenai-finops")
except PackageNotFoundError:  # pragma: no cover - source-tree only
    __version__ = "1.2.6"

__all__ = [
    "AttributionConflict",
    "AttributionContext",
    "BudgetExceeded",
    "BudgetUnavailable",
    "CustomerIdRequired",
    "FinOpsConfig",
    "FinOpsController",
    "InvalidAttribution",
    "KazenBudgetExceeded",
    "KazenCircuitBreaker",
    "KazenEvent",
    "LoopDetected",
    "SharedBudget",
    "StreamCutoffError",
    "UnknownModelError",
    "__version__",
    "aguarded_llm_call",
    "guarded_embedding_call",
    "guarded_llm_call",
    "monitor",
    "new_id",
    "now_ms",
    "use_attribution",
]
