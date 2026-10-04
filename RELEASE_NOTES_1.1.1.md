# kazenai-finops 1.1.1

Compatibility/distribution patch on the Control 1.1.x line. **No runtime capability
matrix widening.**

## What changed and why

- Depends on `kazenai>=1.1.1,<2.0`.
- Adds matching `openai`, `anthropic`, and `providers` extras with certified bounds.
- Synchronizes customer-facing install guidance to bounded extras.

## Install

```bash
python -m pip install "kazenai-finops[openai]==1.1.1"
python -m pip install "kazenai-finops[anthropic]==1.1.1"
python -m pip install "kazenai-finops[providers]==1.1.1"
```

## Supported provider methods and SDK ranges

Identical to Core 1.1.x: sync OpenAI Chat Completions and Anthropic Messages,
non-streaming and selected streaming surfaces.
Ranges: `openai>=1.40,<2`, `anthropic>=0.39,<1`.

`from kazenai_finops import monitor` is an identity re-export of `kazenai.monitor`.

## Explicitly unsupported

Async clients, Responses, Realtime, Bedrock/Vertex, and uncertified provider majors.

## Behavior change

None intended versus 1.1.0 certified surfaces.

## Security / privacy impact

None.

## Upgrade from 1.1.0

Publish/install Core 1.1.1 first, then:

```bash
python -m pip install -U "kazenai-finops[openai]==1.1.1"
```

## Links

- Docs: https://docs.kazenai.com/
- Issues: https://github.com/kazenai-ai/kazenai-finops-sdk/issues
- Source tag: `v1.1.1` (fill commit SHA at publication)

## Known limitation

Streaming cancellation / missing authoritative usage remains pending/unknown,
not exact zero.

## Artifact digests

Record wheel/sdist SHA-256 and PyPI provenance links after Trusted Publishing.
