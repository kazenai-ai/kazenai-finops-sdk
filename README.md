# kazenai-finops

> **A hard spending limit for every customer's AI.**

[![PyPI](https://img.shields.io/pypi/v/kazenai-finops.svg)](https://pypi.org/project/kazenai-finops/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://github.com/kazenai-ai/kazenai-finops-sdk/blob/main/LICENSE)

**Install:** [PyPI · kazenai-finops](https://pypi.org/project/kazenai-finops/) · **Docs:** [docs.kazenai.com](https://docs.kazenai.com/) · **Products:** [kazenai.com](https://kazenai.com)

**Source:** [github.com/kazenai-ai/kazenai-finops-sdk](https://github.com/kazenai-ai/kazenai-finops-sdk)

---

## What is this?

Flat-priced AI has one weak spot: a few customers, or one stuck agent, can cost
more than they pay. KazenAI checks every model call against that customer's
limit before it runs. Over the limit, the call doesn't happen.

`kazenai-finops` is the **customer SDK for Agent FinOps**. Install it, wrap your OpenAI or Anthropic client with `monitor()`, and get:

1. **Pre-call budget deny** — hard `BudgetExceeded` before a provider call
2. **Soft trajectory pause** — `KazenCircuitBreaker` when projected spend trips (alias: `KazenBudgetExceeded`)
3. **Loop detection** — stop repeated high-risk patterns before another LLM call
4. **A limit per customer in Agent FinOps** (optional) — enforced across every process, with a receipt for every allow and deny

It depends on [`kazenai`](https://pypi.org/project/kazenai/) (the core engine) and [`kazen-event-schema`](https://pypi.org/project/kazen-event-schema/). Most teams should install **this** package, not core directly.

```
Traditional tools:  LLM call → response → log cost → dashboard shows overspend
KazenAI:            Pre-flight check → BLOCKED → LLM call never made
```

---

## Install

```bash
python -m pip install "kazenai-finops[openai]==1.2.1"
# Optional Anthropic path:
# python -m pip install "kazenai-finops[anthropic]==1.2.1"
# Both providers:
# python -m pip install "kazenai-finops[providers]==1.2.1"
```

Requires Python 3.10–3.14.

Provider extras keep the provider SDKs within the supported ranges
(`openai>=1.40,<3`, `anthropic>=0.39,<1`). KazenAI is tested on OpenAI 1.109.1
and 2.48.0 (Chat Completions), OpenAI 2.54.0 (Responses and the live runs) and
Anthropic 0.125.0. `kazenai-finops` 1.2.1 installs `kazenai` 1.2.1 or later.

---

## Quick start

```python
from kazenai_finops import monitor, BudgetExceeded, KazenCircuitBreaker
import openai

client = openai.OpenAI(max_retries=0)
monitored = monitor(
    client,
    agent_id="customer-support",
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

### Hosted limits per customer

```bash
export KAZENAI_FINOPS_URL=https://finops.example.com   # your Agent FinOps URL
export KAZENAI_FINOPS_API_KEY=kz_...
export KAZENAI_TIER_MISMATCH_MULTIPLIER=2              # required under Control
```

```python
monitored = monitor(
    client,
    agent_id="customer-support",
    org_id="<organization ID>",      # both IDs are on the Setup page in Agent FinOps
    workspace_id="<workspace ID>",
    max_budget_usd=5.00,
    require_customer_id=True,        # refuse a call that names no customer
)
```

An Agent FinOps API key belongs to one organization and one workspace. Pass the
same two IDs to `monitor()`; the Setup page in Agent FinOps shows them and fills
them into its code snippet. `monitor()` does not read them from the key or from
`KAZENAI_ORG_ID`. Without them it uses `local` and `default`, Agent FinOps
refuses each reservation with HTTP 403, and the call raises `BudgetUnavailable`
before it reaches the provider.

Name the customer on each call. A per-customer limit in Agent FinOps (dimension
`business_subject`) applies only to calls that carry that customer's ID as
`business_subject_ref`:

```python
from kazenai_finops import use_attribution

with use_attribution(business_subject_ref="cust_123"):
    monitored.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Summarize this ticket"}],
    )
```

Use the same ID the limit was set for. When a client only ever serves one
customer, `monitor(..., business_subject_ref="cust_123")` names that customer on
every call instead. If both name a customer and the IDs differ, the call raises
`AttributionConflict` before it reaches the provider. A call without a customer
ID is checked against the organization and workspace limits only; no
per-customer limit applies to it. The ID is held in a context variable: calls in
the same thread, and in asyncio tasks started inside the `with` block, carry it.
A thread started inside the block, such as a `ThreadPoolExecutor` worker, does not.
To carry the ID into a worker, submit the work in a copy of the current context:

```python
import contextvars

with use_attribution(business_subject_ref="cust_123"):
    pool.submit(contextvars.copy_context().run, handle_ticket, ticket)
```

With `require_customer_id=True` (1.2.1 and later), a call without a customer ID
raises `CustomerIdRequired` before it reserves budget or reaches the provider,
instead of being checked against the organization and workspace limits only.

Setting the FinOps URL selects the Control lifecycle (the default since 1.2.0):
each guarded call reserves against your limits in Agent FinOps before dispatch
and settles after it. A refused reservation raises `BudgetExceeded` before the
provider is called, and an unreachable Agent FinOps refuses the call.
`monitor()` refuses to start under Control without
`KAZENAI_TIER_MISMATCH_MULTIPLIER` (finite, at least 1: how much of the
requested-tier price is held when a provider bills an uncertified service tier)
or with a provider client built with retries (use `max_retries=0`). An admin
can pause an organization in Agent FinOps; new reservations are then refused
until it is resumed.

`FinOpsSpendClient.check_budget()` and `reconcile_budget()` call the legacy
endpoints that hosted Agent FinOps refuses under Control. They are deprecated
and raise `LegacyBudgetEndpointUnsupported` against it; use `monitor()`.

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
| OpenAI Responses (`create`, `stream`, `parse`), sync and async, streaming and non-streaming | Supported, verified against the live API (new in 1.2.0). `background=True`, `previous_response_id` / `conversation` / stored `prompt` and built-in tools are refused before dispatch |
| CrewAI 1.15.26 (`kickoff`, `akickoff`, `kickoff_async`) | Supported, verified against the live API, when every LLM is bound with `bind_crew_llm_client` (two providers: `guarded_clients=[...]`). Memory, knowledge, `Crew(stream=True)` and `llm_overlay` are refused under Control; Anthropic structured output is not supported. Cancelling `kickoff_async` does not stop the crew; use `akickoff` |
| OpenAI Realtime, embeddings, images, audio, batches, fine-tuning; any provider method saved before `monitor()` | Refused before dispatch on a monitored client; `monitor(..., allow_unmetered=("/embeddings",))` sends named endpoints without a budget check |
| Anthropic `client.beta.messages`, Bedrock/Vertex wrappers, AutoGen | Not supported |

### Optional framework extras

```bash
pip install 'kazenai-finops[langgraph]'   # or: langchain, crewai, all — see pyproject.toml
```

```python
from kazenai_finops.adapters.langchain import wrap_langchain_runnable
from kazenai_finops.adapters.langgraph import wrap_graph_invoke
from kazenai_finops.adapters.crewai import bind_crew_llm_client, wrap_crew
```

For Control, wrap the actual OpenAI/Anthropic client with `monitor()` and satisfy
the adapter's binding requirement. A separate, unused monitored client does not
protect provider calls made elsewhere in a framework workflow.

```python
from kazenai_finops import SharedBudget
from kazenai_finops.adapters.langchain import bind_monitored_chat_anthropic, bind_monitored_chat_openai

budget = SharedBudget(max_usd=1.00)  # one cap for every step of the workflow
bind_monitored_chat_openai(planner_chat, OpenAI(max_retries=0), async_client=AsyncOpenAI(max_retries=0), budget=budget)
bind_monitored_chat_anthropic(writer_chat, Anthropic(max_retries=0), async_client=AsyncAnthropic(max_retries=0), budget=budget)
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
    openai.OpenAI(max_retries=0),
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
- **Low overhead** — a guarded call adds about three network round trips to
  Agent FinOps over one kept-alive connection: a few milliseconds when your app
  runs in the same cloud region
- **Shared policies fail closed by default** — a call is refused when the
  shared reservation cannot be obtained, unless the organization chose fail-open

The local cap is not an account-wide provider billing limit. Multiple workers
or services need the shared FinOps authority for a cross-process budget.
Fail-open (an organization setting in Agent FinOps) keeps only local safeguards
while Agent FinOps is unreachable.

---

## How it relates to `kazenai`

| Package | Role |
|---------|------|
| [`kazenai-finops`](https://pypi.org/project/kazenai-finops/) | Customer SDK (this package) — recommended install |
| [`kazenai`](https://pypi.org/project/kazenai/) | Core `monitor()` engine |
| [`kazen-event-schema`](https://pypi.org/project/kazen-event-schema/) | Shared event contract |

`from kazenai_finops import monitor` re-exports the core engine so existing integrations keep working.

---

## License

Apache License 2.0. See [LICENSE](https://github.com/kazenai-ai/kazenai-finops-sdk/blob/main/LICENSE) and [NOTICE](https://github.com/kazenai-ai/kazenai-finops-sdk/blob/main/NOTICE).

Issues: https://github.com/kazenai-ai/kazenai-finops-sdk/issues · Products: [kazenai.com](https://kazenai.com) · **founder@kazenai.com**
