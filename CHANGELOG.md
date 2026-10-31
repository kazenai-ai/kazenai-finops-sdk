# Changelog

Notable changes to `kazenai-finops`, newest first. Each release is also published on
[GitHub Releases](https://github.com/kazenai-ai/kazenai-finops-sdk/releases).

## 1.2.1 - 2026-10-31

Name the customer from `kazenai_finops`, and refuse calls that don't.

```bash
python -m pip install "kazenai-finops[openai]==1.2.1"
```

### New

- `kazenai_finops` now exports `use_attribution`, `AttributionConflict` and
  `AttributionContext`, so `from kazenai_finops import use_attribution` works.
- Ships `kazenai` 1.2.1: `monitor(..., require_customer_id=True)` refuses a call
  that names no customer ID with `CustomerIdRequired` (also exported here), before
  it reserves budget or reaches the provider. Off by default.

### Docs

- "Hosted limits per customer" shows the `org_id` and `workspace_id` that hosted
  Agent FinOps needs (without them each reservation gets HTTP 403), how to name
  the customer on each call, and how to carry the ID into a worker thread.

### Compatibility

- Requires `kazenai[server]>=1.2.1,<2` and `kazen-event-schema>=0.6.6,<0.7`.
- Supports Python 3.13 and 3.14, now tested in CI alongside 3.10–3.12 and listed
  in the package metadata.

## 1.2.0 - 2026-10-28

Ships `kazenai` 1.2.0: hard limits by default when Agent FinOps is configured,
an optional per-organization fail-open setting, faster calls to Agent FinOps
over kept-alive connections, the OpenAI Responses API, certified CrewAI support,
and a security fix.
**Upgrade from any earlier release:** 1.0.1 to 1.1.3 let some OpenAI calls skip
the budget check.

```bash
python -m pip install "kazenai-finops[openai]==1.2.0"
```

What's new, what to change before upgrading, and the security details are in
the [kazenai 1.2.0 release notes](https://github.com/kazenai-ai/kazenai-core/releases/tag/v1.2.0).

### Changes in this package

- Requires `kazenai[server]>=1.2.0,<2` and `kazen-event-schema>=0.6.6,<0.7`.
  The `server` extra adds `cryptography`, used to verify signed prices.
- `FinOpsSpendClient.check_budget()` and `reconcile_budget()` are deprecated,
  along with the spend adapters built on them. Hosted Agent FinOps no longer
  accepts those calls, and they now raise `LegacyBudgetEndpointUnsupported`. Use
  `monitor()` instead.

## 1.1.3 - 2026-10-12

Tracks `kazenai` 1.1.3. `kazenai-finops` re-exports `kazenai` and its framework
adapters, so this release includes everything new in `kazenai` 1.1.2 and 1.1.3.

### Changes

- Requires `kazenai>=1.1.3,<2.0` and `kazen-event-schema>=0.6.4,<0.7`.
- Provider extras: `openai>=1.40,<3`, `anthropic>=0.39,<1`.
- Supports OpenAI Chat Completions and Anthropic Messages, sync and async,
  streaming and non-streaming, verified against the live provider APIs. See
  [Supported integrations](https://github.com/kazenai-ai/kazenai-core/blob/main/docs/integrations/control-supported-matrix.md).
  OpenAI Responses/Realtime, Anthropic beta Messages and AutoGen are not
  supported; CrewAI is a preview.
- Removes the non-functional `kazenai_finops.adapters.autogen` module and the
  `autogen` extra. The module imported APIs that do not exist and could not be
  imported; AutoGen remains unsupported.
- Inherits the `kazenai` pricing refresh and its behaviour change:
  unpriced models are blocked before dispatch by default (`UnknownModelError`).
- Re-exports `SharedBudget` (one local cap shared by several `monitor()` clients)
  and, from `kazenai_finops.adapters.langchain`, `bind_monitored_chat_anthropic`
  and `declare_langchain_control_boundary` (several clients per chain).
- Streamed costs are priced on input and output tokens separately; provider
  refusals before any output settle at $0; LangChain non-streaming calls record
  their cost; Anthropic beta Messages are blocked on monitored clients.
- LangChain, LangGraph and LiteLLM paths are verified against the live APIs.
- Clearer documentation; the source distribution ships the package, licence
  and README only.

### Install

```bash
python -m pip install "kazenai-finops[openai]==1.1.3"
```

## 1.1.1 - 2026-10-04

Compatibility/distribution patch on the Control 1.1.x line. **No runtime capability
supported-integration change.**

### What changed and why

- Depends on `kazenai>=1.1.1,<2.0`.
- Adds matching `openai`, `anthropic`, and `providers` extras with supported bounds.
- Synchronizes customer-facing install guidance to bounded extras.

### Install

```bash
python -m pip install "kazenai-finops[openai]==1.1.1"
python -m pip install "kazenai-finops[anthropic]==1.1.1"
python -m pip install "kazenai-finops[providers]==1.1.1"
```

### Supported provider methods and SDK ranges

Identical to Core 1.1.x: sync OpenAI Chat Completions and Anthropic Messages,
non-streaming and selected streaming surfaces.
Ranges: `openai>=1.40,<2`, `anthropic>=0.39,<1`.

`from kazenai_finops import monitor` is an identity re-export of `kazenai.monitor`.

### Explicitly unsupported

Async clients, Responses, Realtime, Bedrock/Vertex, and unsupported provider majors.

### Behavior change

None intended versus 1.1.0.

### Security / privacy impact

None.

### Upgrade from 1.1.0

Publish/install Core 1.1.1 first, then:

```bash
python -m pip install -U "kazenai-finops[openai]==1.1.1"
```

### Links

- Docs: https://docs.kazenai.com/
- Issues: https://github.com/kazenai-ai/kazenai-finops-sdk/issues
- Source tag: `v1.1.1`

### Known limitation

Streaming cancellation / missing authoritative usage remains pending/unknown,
not exact zero.

Earlier releases: [GitHub Releases](https://github.com/kazenai-ai/kazenai-finops-sdk/releases).
