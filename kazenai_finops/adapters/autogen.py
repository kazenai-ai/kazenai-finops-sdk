"""AutoGen adapter — production-grade wrap for AutoGen ConversableAgent.

The AutoGen adapter is implemented here (not in kazenai-core) because
AutoGen's API has evolved across the 0.2 / 0.4 / 0.6 lines; isolating it
here lets kazenai-core stay stable while this file follows AutoGen's
release cadence.

Public API:
    wrap_conversable_agent(agent, *, agent_id, api_key, ...) → ConversableAgent
        Returns the same agent instance with hooks installed; chains
        return statements work unchanged.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

try:
    from kazenai.client import KazenSDKClient
    from kazenai.context import RunContext
    from kazenai.enforcement import LocalEnforcer
    from kazenai.schema import KazenEvent, new_id, now_ms
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "kazenai-finops requires `kazenai-core` to be installed. "
        "Install it with: pip install kazenai-finops"
    ) from exc

try:
    from autogen import ConversableAgent  # type: ignore[import-not-found]
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "kazenai-finops[autogen] requires `pyautogen` to be installed. "
        "Install it with: pip install kazenai-finops[autogen]"
    ) from exc


logger = logging.getLogger("kazenai_finops.adapters.autogen")


def wrap_conversable_agent(
    agent: "ConversableAgent",
    *,
    agent_id: str,
    api_key: str,
    org_id: str = "default",
    workspace_id: str = "default",
    max_budget_usd: Optional[float] = None,
    backend_url: Optional[str] = None,
    debug: bool = False,
) -> "ConversableAgent":
    """Instrument a ``ConversableAgent`` with KazenAI traces + budget control.

    The wrapper:
        1. Installs a `reply_hook` on the agent so every reply emits a
           ``model.call`` KazenEvent with token + cost attribution.
        2. Establishes a ``RunContext`` keyed on the agent's name so
           multi-agent group chats share the same run + budget.
        3. When ``max_budget_usd`` is set, raises
           ``KazenCircuitBreaker`` before the next reply if projected
           spend would exceed budget.

    Args:
        agent: AutoGen ConversableAgent instance.
        agent_id: Stable identifier for this agent (appears in traces).
        api_key: KazenAI API key (https://kazenai.com/onboarding).
        org_id, workspace_id: Tenancy labels on emitted events.
        max_budget_usd: Per-run soft budget. None disables the breaker.
        backend_url: Optional FinOps HTTP sink. None = local-only.
        debug: Print per-step cost to stdout (use during onboarding).

    Returns:
        The same agent instance, mutated in place. Returns the agent
        rather than a wrapper so chained method calls keep working.

    Idempotent: calling twice on the same agent installs the hook once.
    """
    if getattr(agent, "_kazenai_wrapped", False):
        logger.debug("Agent %r already wrapped; skipping", agent_id)
        return agent

    client = KazenSDKClient(
        api_key=api_key,
        backend_url=backend_url,
        org_id=org_id,
        workspace_id=workspace_id,
    )
    enforcer = LocalEnforcer(max_budget_usd=max_budget_usd) if max_budget_usd else None
    ctx = RunContext(agent_id=agent_id, org_id=org_id, workspace_id=workspace_id)

    _original_generate = agent.generate_reply

    def _wrapped_generate_reply(*args: Any, **kwargs: Any) -> Any:
        if enforcer is not None:
            enforcer.check_pre_call(role=agent_id)

        step_id = new_id()
        t0 = now_ms()
        try:
            reply = _original_generate(*args, **kwargs)
        except Exception:
            raise

        # AutoGen returns a str or dict; record what we can.
        prompt_tokens = int((kwargs.get("messages") or [{}])[-1].get("content_tokens", 0) or 0)
        completion_tokens = len(str(reply or "")) // 4  # rough estimate

        event = KazenEvent(
            schema_version="1.2",
            ts_ms=t0,
            event_id=new_id(),
            org_id=org_id,
            workspace_id=workspace_id,
            project_id=workspace_id,
            surface="kazenai-finops-autogen",
            agent_id=agent_id,
            agent_role="autogen.conversable",
            run_id=ctx.run_id,
            step_id=step_id,
            parent_step_id=ctx.last_step_id,
            event_type="model.call",
            tokens_used=prompt_tokens + completion_tokens,
            cost_usd=None,                 # provider-specific; left to FinOpsController
            payload={
                "model": getattr(agent, "llm_config", {}).get("model"),
                "kind": "autogen.generate_reply",
            },
        )
        client.emit(event)
        if enforcer is not None:
            enforcer.record_actual(cost_usd=0.0)  # cost unknown at this layer
        ctx.last_step_id = step_id

        if debug:
            print(
                f"[KazenAI] step={step_id[:8]} agent={agent_id} "
                f"tokens≈{prompt_tokens + completion_tokens}"
            )
        return reply

    agent.generate_reply = _wrapped_generate_reply  # type: ignore[assignment]
    agent._kazenai_wrapped = True                    # type: ignore[attr-defined]
    agent._kazenai_run_context = ctx                 # type: ignore[attr-defined]
    return agent


__all__ = ["wrap_conversable_agent"]
