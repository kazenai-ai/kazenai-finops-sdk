# kazenai-finops 1.1.3

Tracks `kazenai` 1.1.3. `kazenai-finops` re-exports `kazenai` and its framework
adapters, so this release includes everything new in `kazenai` 1.1.2 and 1.1.3.

## Changes

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

## Install

```bash
python -m pip install "kazenai-finops[openai]==1.1.3"
```
