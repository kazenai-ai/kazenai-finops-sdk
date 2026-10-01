# PyPI 1.1.0 release evidence checklist

This file is a checklist for the coordinated 1.1.0 release. It does not claim
that an artifact has been uploaded or verified. Record evidence only after the
corresponding command has completed successfully.

## Candidate versions

| Distribution | Required version | Release dependency |
|---|---:|---|
| `kazen-event-schema` | `>=0.6.3,<0.7` | Must resolve from public PyPI or the reviewed vendored CI artifact |
| `kazenai` | `1.1.0` | Must be published and clean-installable before FinOps CI/release |
| `kazenai-finops` | `1.1.0` | Publish only after the public Core prerequisite passes |

## Core prerequisite evidence

- [ ] Core release commit SHA recorded: `<SHA>`
- [ ] Core CI URL recorded; Python 3.10, 3.11 and 3.12 all passed: `<URL>`
- [ ] `kazenai==1.1.0` built from a clean checkout
- [ ] `python -m twine check` passed for both Core artifacts
- [ ] Core wheel/sdist SHA-256 hashes recorded: `<HASHES>`
- [ ] Public `pip install --no-cache-dir kazenai==1.1.0` passed in a clean environment
- [ ] Installed Core smoke test passed without a sibling checkout or `PYTHONPATH`

## FinOps source and CI evidence

- [ ] `pyproject.toml` version is `1.1.0`
- [ ] `kazenai_finops.__version__` fallback is `1.1.0`
- [ ] Dependency is `kazenai>=1.1.0,<2.0`
- [ ] Release commit SHA recorded: `<SHA>`
- [ ] Working tree was clean at the recorded SHA
- [ ] CI URL recorded; Python 3.10, 3.11 and 3.12 all passed: `<URL>`
- [ ] CI resolved Core through the public dependency rather than a sibling checkout

## Clean build evidence

From a fresh clone of the recorded FinOps commit:

```bash
python3 -m venv .venv-release
source .venv-release/bin/activate
python -m pip install --upgrade pip build twine
python -m build
python -m twine check dist/*
```

- [ ] Wheel check passed: `dist/kazenai_finops-1.1.0-py3-none-any.whl`
- [ ] Source distribution check passed: `dist/kazenai_finops-1.1.0.tar.gz`
- [ ] Wheel/sdist SHA-256 hashes recorded: `<HASHES>`
- [ ] Wheel installed in a second clean environment against public `kazenai==1.1.0`
- [ ] Package metadata reported Core and FinOps versions `1.1.0 1.1.0`

## Installed-wheel behavior evidence

- [ ] Package import and public re-exports passed
- [ ] Sync OpenAI non-streaming smoke passed
- [ ] Sync OpenAI `create(stream=True)` smoke passed
- [ ] Sync OpenAI `chat.completions.stream(...)` manager smoke passed
- [ ] Sync Anthropic non-streaming smoke passed
- [ ] Sync Anthropic `messages.stream(...)` manager smoke passed
- [ ] Pre-dispatch budget denial made no provider call
- [ ] Successful stream produced exactly one reservation/finalization lifecycle
- [ ] Cancelled/error/missing-usage stream remained pending/outcome-unknown, not exact zero
- [ ] No test relied on editable installs, repository imports or local package indexes

## Publication and public verification

- [ ] PyPI Trusted Publishing workflow/run recorded, or manual upload approval recorded: `<URL/NOTE>`
- [ ] `kazenai-finops==1.1.0` is visible on public PyPI
- [ ] Fresh `--no-cache-dir` install of both exact versions passed
- [ ] Final public-PyPI smoke test passed
- [ ] Published commit tag and GitHub Release created
- [ ] Demo pins updated only after public verification
- [ ] Matching docs revision deployed

The operational commands and release ordering are maintained in
[RELEASING.md](RELEASING.md).
