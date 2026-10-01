# kazenai-finops

> **Stop your AI agents from burning your budget. Catch loops before they catch you.**

[![PyPI](https://img.shields.io/pypi/v/kazenai-finops.svg)](https://pypi.org/project/kazenai-finops/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

**Install:** [PyPI · kazenai-finops](https://pypi.org/project/kazenai-finops/) · **Docs:** [docs.kazenai.com](https://docs.kazenai.com/) · **Products:** [kazenai.com](https://kazenai.com)

**Source:** [github.com/kazenai-ai/kazenai-finops-sdk](https://github.com/kazenai-ai/kazenai-finops-sdk)

---

## What is this?

`kazenai-finops` is the **customer-facing Agent FinOps SDK**. Install it, wrap your OpenAI or Anthropic client with `monitor()`, and get:

1. **Pre-call budget deny** — hard `BudgetExceeded` before a provider call
2. **Soft trajectory pause** — `KazenCircuitBreaker` when projected spend trips (alias: `KazenBudgetExceeded`)
3. **Loop detection** — stop repeated high-risk patterns before another LLM call
4. **Optional FinOps / Lens evidence** — canonical `KazenEvent` batches when ingest is configured

It depends on [`kazenai`](https://pypi.org/project/kazenai/) (the core engine) and [`kazen-event-schema`](https://pypi.org/project/kazen-event-schema/). Most teams should install **this** package, not core directly.

```
Traditional tools:  LLM call → response → log cost → dashboard shows overspend
KazenAI:            Pre-flight check → BLOCKED → LLM call never made
```

---

## Install

```bash
python -m pip install kazenai-finops openai
# Optional Anthropic path:
# python -m pip install kazenai-finops anthropic
```

Requires Python 3.10–3.12.

---

## Quick start

```python
from kazenai_finops import monitor, BudgetExceeded, KazenCircuitBreaker
import openai

client = openai.OpenAI()
monitored = monitor(
    client,
    agent_id="customer-support",
    # Optional ingest: set KAZENAI_FINOPS_API_KEY / KAZENAI_FINOPS_URL in the environment
    max_budget_usd=5.00,
    debug=True,
)

try:
    for i in range(100):
        monitored.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Step {i}"}],
        )
except BudgetExceeded as e:
    print(f"Hard cap (before provider): {e}")
except KazenCircuitBreaker as e:
    print(f"Soft pause (after a completed call): {e}")
```

Call sites stay the same — `monitor()` wraps the client.

---

## Supported today

| Path | Status |
|------|--------|
| Sync OpenAI `chat.completions.create` (non-streaming and `stream=True`) / `chat.completions.stream` | Supported via `monitor()` |
| Sync Anthropic `messages.create` / `messages.stream` | Supported via `monitor()` |
| OpenAI Responses / async / Realtime | Unsupported on the Control path |
| LangChain / LangGraph / CrewAI / AutoGen adapters | Optional extras for evaluation — prefer wrapping the underlying client with `monitor()` |

### Optional framework extras

```bash
pip install 'kazenai-finops[langgraph]'   # similarly: langchain, crewai, etc. — see pyproject.toml
```

```python
from kazenai_finops.adapters.langchain import wrap_langchain_runnable
from kazenai_finops.adapters.langgraph import wrap_graph_invoke
from kazenai_finops.adapters.crewai import wrap_crew_kickoff
```

These helpers are for evaluation. For the supported control path, wrap the OpenAI/Anthropic client with `monitor()`.

---

## Streaming (Control-certified)

Streaming uses the same pre-dispatch reservation. At provider dispatch the
reservation becomes `provider_started`. Settlement happens when the stream ends
with authoritative usage; early `close()`, a provider error, or missing final
usage becomes `outcome_unknown` and leaves shared reconciliation pending rather
than recording an exact zero or releasing an already-started call.

```python
from kazenai_finops import monitor, StreamCutoffError
import openai

monitored = monitor(
    openai.OpenAI(),
    agent_id="streaming-agent",
    max_budget_usd=1.00,
    stream_cutoff_usd=0.50,  # optional local cutoff (does not use /v1/budget/stream-tick)
)

try:
    stream = monitored.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Long answer please"}],
        stream=True,
    )
    with stream:
        for chunk in stream:
            ...
except StreamCutoffError as e:
    print(f"Stream cut at ${e.blocked_usd:.6f}")
```

The official lazy OpenAI helper is supported too. Dispatch occurs when its
context manager is entered, and the nested SDK call is accounted for exactly
once:

```python
with monitored.chat.completions.stream(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Long answer please"}],
) as stream:
    for event in stream:
        ...
```

`stream_enforcement=True` is deprecated; prefer `stream_cutoff_usd`. The cutoff
uses output observable at the client. It cannot see hidden reasoning or guarantee
that the provider stopped generating or billing immediately after the close.

---

## Local and shared enforcement

- **Local hard cap works offline** — no FinOps round-trip is required for the
  in-process client limit
- **Low overhead** — checks stay on the hot path
- **Shared policies can fail closed** — production/staging modes deny when a
  required shared reservation cannot be obtained

The local cap is not an account-wide provider billing limit. Multiple workers
or services need the shared FinOps authority for a cross-process budget. An
explicit development fail-open path retains only local safeguards.

---

## How it relates to `kazenai`

| Package | Role |
|---------|------|
| [`kazenai-finops`](https://pypi.org/project/kazenai-finops/) | Customer SDK (this package) — recommended install |
| [`kazenai`](https://pypi.org/project/kazenai/) | Core `monitor()` engine |
| [`kazen-event-schema`](https://pypi.org/project/kazen-event-schema/) | Shared event contract |

`from kazenai_finops import monitor` re-exports the core engine so existing integrations keep working.

Maintainers: follow [RELEASING.md](RELEASING.md). Core 1.1.0 must be available
on public PyPI before this package's 1.1.0 CI, clean build and publication.

---

## License

Apache License 2.0. See LICENSE and NOTICE.

Issues: https://github.com/kazenai-ai/kazenai-finops-sdk/issues · Products: [kazenai.com](https://kazenai.com) · **founder@kazenai.com**
