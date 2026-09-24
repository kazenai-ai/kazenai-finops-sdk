# kazenai-finops

> **Control FINAL_1 scope:** Only sync OpenAI Chat Completions + Anthropic Messages via `kazenai.monitor` / `kazenai_finops.monitor` are Control-certified (see `docs/integrations/control-supported-matrix.md`). Framework adapters, streaming mid-flight cutoff, and durable checkpoint/resume are **shipped as extras or experimental paths** — not Control-supported unless a matrix cell is raised with evidence.

[![PyPI](https://img.shields.io/pypi/v/kazenai-finops.svg)](https://pypi.org/project/kazenai-finops/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Stop your AI agents from burning your budget. Catch loops before they catch you.**

**Install:** [PyPI · kazenai-finops](https://pypi.org/project/kazenai-finops/) · **Products:** [kazenai.com](https://kazenai.com)

`kazenai-finops` is the customer-facing Agent FinOps SDK. It wraps supported LLM clients and adds budget enforcement, loop detection, and optional event ingest for Agent FinOps / Agent Lens.

**Published on PyPI** as `kazenai-finops` (depends on `kazenai` and `kazen-event-schema`). Prefer `pip install kazenai-finops`. Editable sibling installs below are for workspace contributors only.

What the Control-certified path provides today:

1. **Pre-call budget deny** — hard `BudgetExceeded` before a provider call when the configured cap would be exceeded.
2. **Soft trajectory pause** — `KazenCircuitBreaker` after a completed call when projection trips (alias: `KazenBudgetExceeded`).
3. **Loop detection** — blocks repeated high-risk patterns before another provider call.
4. **Optional FinOps ingest** — canonical `KazenEvent` batches when `KAZENAI_FINOPS_URL` / API key are set (HttpSink).

```python
# pip install kazenai-finops openai
from kazenai_finops import monitor, BudgetExceeded
import openai

client = openai.OpenAI()
monitored = monitor(
    client,
    agent_id="customer-support",
    # set KAZENAI_FINOPS_API_KEY in the environment (not a monitor kwarg)
    max_budget_usd=5.00,
    debug=True,
)
# Certified Control path: sync chat.completions.create (non-streaming).
```

---

## Installation

```bash
python -m pip install kazenai-finops openai
# Optional Anthropic path:
# python -m pip install kazenai-finops anthropic
```

Requires Python 3.10–3.12. Also installs transitive `kazenai` and `kazen-event-schema`.

### Workspace / contributor install (optional)

From a full KazenAI workspace checkout:

```bash
python -m venv .venv-finops-sdk
. .venv-finops-sdk/bin/activate
pip install -e ./kazen-event-schema
pip install --no-deps -e ./kazenai-core
pip install -e ./kazenai-finops-sdk
```

Optional extras are defined in `pyproject.toml`, for example
`pip install 'kazenai-finops[langgraph]'` (framework adapters — **not** Control-certified in FINAL_1).

---

## Quick Start

### Raw OpenAI (Control-certified)

```python
from kazenai_finops import monitor, BudgetExceeded, KazenCircuitBreaker
import openai

client = openai.OpenAI()
monitored = monitor(
    client,
    agent_id="my-agent",
    # KAZENAI_FINOPS_API_KEY env — https://kazenai.com
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

### Framework adapters (not Control-certified)

These helpers exist in the package for evaluation. They are **not** FINAL_1 Control-certified. Prefer wrapping the underlying OpenAI/Anthropic client with `monitor()` for the supported path.

```python
# Optional extras — see pyproject.toml [project.optional-dependencies]
from kazenai_finops.adapters.langchain import wrap_langchain_runnable
from kazenai_finops.adapters.langgraph import wrap_graph_invoke
from kazenai_finops.adapters.crewai import wrap_crew_kickoff
from kazenai_finops.adapters.autogen import wrap_conversable_agent
```

---

## Mid-stream budget enforcement (SSE)

> **Not Control-certified** in FINAL_1. Streaming / mid-flight cutoff is an experimental path.

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

Most observability tools record what happened. **KazenAI can block what's about to happen** on the certified sync path.

```
Traditional tools:  LLM call → response → log cost → dashboard shows overspend
KazenAI (local):    Pre-flight check → BLOCKED → LLM call never made
```

Local enforcement means:
- **Works offline for the hard cap** — no FinOps network round-trip required to deny
- **Low overhead** — budget check completes locally on the hot path
- **Backend outage ≠ unprotected spend** for the local hard-cap path — optional ingest may still fail open depending on configuration

---

## How it relates to `kazenai` (core)

`kazenai-finops` is the *customer-facing* package name on PyPI. It re-exports and depends on [`kazenai`](https://pypi.org/project/kazenai/) (this workspace’s `kazenai-core` repo), which provides `monitor()`, enforcement primitives, and shared wiring to [`kazen-event-schema`](https://pypi.org/project/kazen-event-schema/). Integrators who need lower-level APIs may depend on `kazenai` directly.

---

## Roadmap (honesty)

| Status | What |
|---|---|
| **Control-certified now** | Sync OpenAI Chat Completions + Anthropic Messages via `monitor()` |
| **In package, not Control-certified** | LangChain / LangGraph / CrewAI / AutoGen adapters; streaming mid-flight |
| **Product / future** | Broader dashboard and investigation surfaces — see product site; not claimed as SDK certification |

Do not treat optional adapters or future roadmap items as Control-supported without matrix evidence.

---

## License

Licensed under the Apache License, Version 2.0. See LICENSE and NOTICE.

Issues and feedback: https://github.com/KazenAI/kazenai-finops/issues

Products and design-partner enquiries: https://kazenai.com · founder@kazenai.com
