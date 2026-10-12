# kazenai-finops

> **Stop your AI agents from burning your budget. Catch loops before they catch you.**

[![PyPI](https://img.shields.io/pypi/v/kazenai-finops.svg)](https://pypi.org/project/kazenai-finops/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/kazenai-ai/kazenai-finops-sdk/blob/main/LICENSE)

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
python -m pip install "kazenai-finops[openai]==1.1.3"
# Optional Anthropic path:
# python -m pip install "kazenai-finops[anthropic]==1.1.3"
# Both providers:
# python -m pip install "kazenai-finops[providers]==1.1.3"
```

Requires Python 3.10–3.12.

Provider extras keep the provider SDKs within the supported ranges
(`openai>=1.40,<3`, `anthropic>=0.39,<1`). KazenAI is tested on OpenAI 1.109.1
and 2.48.0 and Anthropic 0.125.0. `kazenai-finops` 1.1.3 installs `kazenai` 1.1.3.

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

Every path below is covered by the test suite; the OpenAI, Anthropic, LiteLLM,
LangChain and LangGraph paths are also verified against the live provider APIs.
Full list: [Supported integrations](https://github.com/kazenai-ai/kazenai-core/blob/main/docs/integrations/control-supported-matrix.md).

| Path | Status |
|------|--------|
| OpenAI Chat Completions (`create`, `stream`, `parse`), sync and async, streaming and non-streaming | Supported, verified against the live API |
| Anthropic Messages (`create`, `stream`), sync and async, streaming and non-streaming | Supported, verified against the live API |
| LangChain `ChatOpenAI` / `ChatAnthropic` | Supported when bound with `bind_monitored_chat_openai` / `bind_monitored_chat_anthropic` |
| LangGraph | Supported when the graph declares every provider client its nodes use; raw clients created inside nodes are not intercepted |
| LiteLLM proxy | Supported with application-owned or gateway-owned accounting (gateway-owned streaming settlement not yet verified) |
| CrewAI | Preview: `bind_crew_llm_client` works for sequential crews; not yet a supported path |
| OpenAI Responses / Realtime, Anthropic `client.beta.messages`, AutoGen | Not supported |

### Optional framework extras

```bash
pip install 'kazenai-finops[langgraph]'   # similarly: langchain, crewai, etc. — see pyproject.toml
```

```python
from kazenai_finops.adapters.langchain import wrap_langchain_runnable
from kazenai_finops.adapters.langgraph import wrap_graph_invoke
from kazenai_finops.adapters.crewai import wrap_crew_kickoff
```

For Control, wrap the actual OpenAI/Anthropic client with `monitor()` and satisfy
the adapter's binding requirement. A separate, unused monitored client does not
protect provider calls made elsewhere in a framework workflow.

```python
from kazenai_finops import SharedBudget
from kazenai_finops.adapters.langchain import bind_monitored_chat_anthropic, bind_monitored_chat_openai

budget = SharedBudget(max_usd=1.00)  # one cap for every step of the workflow
bind_monitored_chat_openai(planner_chat, OpenAI(), async_client=AsyncOpenAI(), budget=budget)
bind_monitored_chat_anthropic(writer_chat, Anthropic(), async_client=AsyncAnthropic(), budget=budget)
```

A LangGraph graph whose nodes call several providers declares all of them with
`declare_langgraph_control_boundary(graph, *clients)` and is wrapped with
`wrap_graph(graph, capability="control", guarded_clients=[...])`.

Pending settlement recovery also requires a persistent
`KAZENAI_SDK_SETTLE_QUEUE_DIR` and a supervised caller of
`flush_pending_settlements`. Use one process per queue directory until the
multiprocess conflict path is made transactional.

---

## Streaming

Streaming uses the same pre-dispatch reservation. At provider dispatch the
reservation becomes `provider_started`. Settlement happens when the stream ends
with authoritative usage; early `close()`, a provider error after dispatch, or
missing final usage becomes `outcome_unknown` and leaves shared reconciliation
pending rather than recording an exact zero or releasing an already-started call.
A definitive provider refusal before any output (HTTP 4xx such as unknown model,
invalid key or rate limit) settles at exactly $0 instead.

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

Maintainers release with [RELEASING.md](https://github.com/kazenai-ai/kazenai-finops-sdk/blob/main/RELEASING.md).

---

## License

Apache License 2.0. See [LICENSE](https://github.com/kazenai-ai/kazenai-finops-sdk/blob/main/LICENSE) and [NOTICE](https://github.com/kazenai-ai/kazenai-finops-sdk/blob/main/NOTICE).

Issues: https://github.com/kazenai-ai/kazenai-finops-sdk/issues · Products: [kazenai.com](https://kazenai.com) · **founder@kazenai.com**
