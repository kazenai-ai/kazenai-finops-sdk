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
    monitor(...)              — wrap sync OpenAI Chat Completions / Anthropic Messages
    BudgetExceeded            — hard local/shared budget deny (before provider)
    BudgetUnavailable         — FinOps unreachable under fail-closed
    KazenCircuitBreaker       — soft trajectory pause (after a completed call)
    KazenBudgetExceeded       — deprecated alias of KazenCircuitBreaker (not hard BudgetExceeded)
    KazenEvent                — canonical event schema (re-export)
    FinOpsController          — lower-level controller for power users
"""

from __future__ import annotations

# Re-export the core public API. Customers import from kazenai_finops; the
# engine lives in kazenai-core. If a user upgrades only kazenai-core they
# still get the new behaviour through this re-export.
from kazenai import monitor                                        # noqa: F401
from kazenai.circuit_breaker import KazenCircuitBreaker            # noqa: F401
from kazenai.enforcement import BudgetExceeded, BudgetUnavailable, StreamCutoffError  # noqa: F401
from kazenai.spine import aguarded_llm_call, guarded_embedding_call, guarded_llm_call  # noqa: F401
from kazenai.finops import FinOpsConfig, FinOpsController          # noqa: F401
from kazenai.schema import KazenEvent, new_id, now_ms              # noqa: F401

# Deprecated alias: soft circuit-breaker only. Hard caps raise BudgetExceeded.
KazenBudgetExceeded = KazenCircuitBreaker

__version__ = "1.0.2"

__all__ = [
    "FinOpsConfig",
    "FinOpsController",
    "KazenBudgetExceeded",
    "KazenCircuitBreaker",
    "KazenEvent",
    "BudgetExceeded",
    "BudgetUnavailable",
    "__version__",
    "aguarded_llm_call",
    "guarded_embedding_call",
    "guarded_llm_call",
    "monitor",
    "new_id",
    "now_ms",
    "StreamCutoffError",
]
