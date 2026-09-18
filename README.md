# kazenai-finops

> **Control FINAL_1 scope:** Only sync OpenAI Chat Completions + Anthropic Messages via `kazenai.monitor` are Control-certified (see `docs/integrations/control-supported-matrix.md`). Claims below about wrapping *any* client, streaming mid-flight, durable checkpoint/resume, or framework “Phase 1 ✓” are **not Control-supported** unless a matrix cell is raised with evidence.


[![Local package](https://img.shields.io/badge/package-local%20v1.0.1-blue.svg)](../WORKSPACE.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![LLM calls guarded](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/kazenai-ai/kazenai-finops-sdk/main/badge/llm-guard.json)](https://github.com/kazenai-ai/kazenai-finops-sdk/blob/main/scripts/audit_llm_calls_all.py)
[![CI](https://img.shields.io/badge/ci-pending%20repo%20setup-lightgrey.svg)](../docs/version_control_reality_plan.md)

> **Stop your AI agents from burning your budget. Catch loops before they catch you.**

**Quickstart:** [kazenai.com/onboarding](https://kazenai.com/onboarding)

`kazenai-finops` is the customer-facing SDK for the KazenAI reliability platform. It wraps any LLM client (OpenAI, Anthropic, LangChain, LangGraph, CrewAI, AutoGen) and adds three capabilities that don't exist elsewhere.

Publishing status: this workspace version is not yet published on PyPI. Use the
local install command below until the package release workflow is moved into a
real repo and run.

1. **Pre-emptive cost circuit-breaker** — pauses your agent before it exceeds budget, preserving state for resume.
2. **Real-time per-step traces** — every LLM and tool call emits a canonical `KazenEvent` to the AgentLens timeline.
3. **Loop detection** — catches the Denial-of-Wallet pattern that no logging tool can stop.

```python
# local checkout install; not yet a PyPI install
from kazenai_finops import monitor
import openai

client = openai.OpenAI()
monitored = monitor(
    client,
    agent_id="customer-support",
    # set KAZENAI_FINOPS_API_KEY in the environment (not a monitor kwarg)
    max_budget_usd=5.00,
    debug=True,
)
# Any call on `monitored` is now traced + budget-guarded.
```

---

## Installation

From the workspace root:

```bash
python -m venv .venv-finops-sdk
. .venv-finops-sdk/bin/activate
pip install -e ./kazen-event-schema
pip install --no-deps -e ./kazenai-core
pip install -e ./kazenai-finops-sdk
```

Optional extras are defined in `pyproject.toml` and can be installed from the
local path, for example `pip install -e './kazenai-finops-sdk[langgraph]'`.

Requires Python 3.10–3.12. No C extensions. Installs in under 30 seconds.

---

## Quick Start

### Raw OpenAI

```python
from kazenai_finops import monitor, BudgetExceeded, KazenCircuitBreaker
import openai

client = openai.OpenAI()
monitored = monitor(
    client,
    agent_id="my-agent",
    # KAZENAI_FINOPS_API_KEY env — https://kazenai.com/onboarding
    max_budget_usd=0.50,
    debug=True,
)

try:
    for i in range(100):
        response = monitored.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Step {i}"}],
        )
except BudgetExceeded as e:  # hard pre-call cap
    print(f"Hard cap: {e}")
except KazenCircuitBreaker as e:  # soft post-call pause (alias: KazenBudgetExceeded)
    print(f"Soft pause: {e}")
```

### LangChain

```python
from kazenai_finops import monitor
from kazenai_finops.adapters.langchain import wrap_langchain_runnable

chain = your_lcel_chain
monitored = wrap_langchain_runnable(chain, agent_id="support", api_key="kz_...")
result = monitored.invoke({"input": "help"})
```

### LangGraph

```python
from kazenai_finops.adapters.langgraph import wrap_graph_invoke

graph = your_graph
monitored = wrap_graph_invoke(graph, agent_id="research-crew", api_key="kz_...")
result = monitored.invoke({"topic": "ai trends"})
```

### CrewAI

```python
from kazenai_finops.adapters.crewai import wrap_crew_kickoff

crew = YourCrew()
monitored = wrap_crew_kickoff(crew, agent_id="research", api_key="kz_...")
result = monitored.kickoff(inputs={"topic": "trends"})
```

### AutoGen

```python
from kazenai_finops.adapters.autogen import wrap_conversable_agent

agent = your_autogen_agent
monitored = wrap_conversable_agent(agent, agent_id="autogen-team", api_key="kz_...")
```

---

## Mid-stream budget enforcement (SSE)

For streaming completions (`stream=True`), enable FinOps mid-flight cutoff so spend is
checked on every token batch — not only at call start:

```python
from kazenai_finops import monitor, StreamCutoffError
import openai

client = openai.OpenAI()
monitored = monitor(
    client,
    agent_id="streaming-agent",
    # set KAZENAI_FINOPS_API_KEY in the environment (not a monitor kwarg)
    max_budget_usd=1.00,
    stream_enforcement=True,  # POST /v1/budget/stream-tick during SSE
)

try:
    stream = monitored.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Long answer please"}],
        stream=True,
    )
    for chunk in stream:
        ...
except StreamCutoffError as e:
    print(f"Stream severed at ${e.blocked_usd:.6f} ({e.total_tokens} tokens)")
```

Set `KAZENAI_FINOPS_URL` and `KAZENAI_FINOPS_STREAM_ENFORCE=1` on the orchestrator for
the same behavior on `stream_model()` chat paths.

---

## Why local-first enforcement matters

Most observability tools record what happened. **KazenAI blocks what's about to happen.**

```
Traditional tools:  LLM call → response → log cost → dashboard shows $47K
KazenAI:            Pre-flight check → BLOCKED → LLM call never made
```

Local enforcement means:
- **No network dependency** — works with `backend_url=None`
- **<5ms overhead** — budget check completes locally
- **Backend outage ≠ protection failure** — the agent doesn't need to reach our servers to be protected

---

## How it relates to `kazenai-core`

`kazenai-finops` is the *customer-facing* package. Under the hood it depends on `kazenai-core`, which provides the framework hooks, event schema, and enforcement primitives. Until publishing is complete, use local sibling-path installs; package authors / integrators may depend on `kazenai-core` directly for finer-grained control.

---

## Roadmap

| Phase | What | When |
|---|---|---|
| Phase 1 | LangChain ✓ · LangGraph ✓ · CrewAI ✓ · AutoGen ✓ · OpenAI ✓ | Now |
| Phase 2 | AgentLens P1 dashboard | Aug 2026 |
| Phase 3 | Probabilistic Replay Engine | Feb 2027 |
| Phase 4 | Semantic Drift Monitor (P3) · TypeScript SDK | Jun 2027 |

---

## License

Licensed under the Apache License, Version 2.0. See LICENSE and NOTICE.

Issues, PRs, and feedback: https://github.com/KazenAI/kazenai-finops/issues

Early access + onboarding: https://kazenai.com

