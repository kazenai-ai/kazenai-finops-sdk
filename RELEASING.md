# Releasing `kazenai-finops`

`kazenai-finops` is the customer-facing SDK. Version 1.1.1 depends on
`kazenai>=1.1.1,<2.0`, so public Core publication and verification are hard
prerequisites—not parallel release tasks.

## Required release order

1. Commit and push the reviewed `kazenai-core` source.
2. Require Core CI to pass on Python 3.10, 3.11 and 3.12.
3. Build Core from a clean checkout, publish `kazenai==1.1.1`, and verify a
   clean public-PyPI install.
4. Commit and push the reviewed `kazenai-finops-sdk` source.
5. Require this repository's CI to pass on Python 3.10, 3.11 and 3.12.
6. Build from a clean checkout and publish `kazenai-finops==1.1.1`.
7. Clean-install both public packages and rerun the supported smoke test.
8. Update demo pins and deploy the matching documentation revision.

Do not publish this package while its required Core version exists only in a
local sibling checkout.

## 1. Confirm the public prerequisite

In a fresh virtual environment, prove that public PyPI resolves the intended
Core and schema versions without an editable install or private package index:

```bash
python3 -m venv .venv-prerequisite
source .venv-prerequisite/bin/activate
python -m pip install --upgrade pip
python -m pip install --no-cache-dir "kazenai==1.1.1" "kazen-event-schema>=0.6.3,<0.7"
python -c "import importlib.metadata as m; print(m.version('kazenai'))"
```

The command must print `1.1.1`.

## 2. Prepare one releasable FinOps commit

- `pyproject.toml` and `kazenai_finops/__init__.py` must both report `1.1.1`.
- The Core dependency must remain `kazenai>=1.1.1,<2.0`.
- README examples and the supported-path table must match the released Core.
- The working tree must contain no secrets, customer data, virtual
  environments, stale build artifacts or unrelated changes.
- Commit and push the reviewed source, then record the exact commit SHA.

Never publish from an uncommitted working tree and never reuse a version that
already exists on PyPI.

## 3. Require the full CI matrix

Wait for GitHub Actions to pass on Python 3.10, 3.11 and 3.12. CI intentionally
installs Core through the public dependency declaration; it must not depend on
`../kazenai-core` or `PYTHONPATH`.

Do not continue if a required job is skipped, cancelled or failing.

## 4. Build from a clean checkout

Clone and check out the exact reviewed FinOps commit:

```bash
git clone https://github.com/kazenai-ai/kazenai-finops-sdk.git kazenai-finops-release
cd kazenai-finops-release
git checkout <RELEASE_COMMIT_SHA>
python3 -m venv .venv-release
source .venv-release/bin/activate
python -m pip install --upgrade pip build twine
python -m build
python -m twine check dist/*
```

Confirm `dist/` was empty before the build and contains only the wheel and source
distribution produced from this commit.

## 5. Test the wheel against public Core

Install the built FinOps wheel into another empty environment. Do not add either
repository to `PYTHONPATH`:

```bash
python3 -m venv .venv-wheel
source .venv-wheel/bin/activate
python -m pip install --upgrade pip
python -m pip install --no-cache-dir dist/kazenai_finops-1.1.1-py3-none-any.whl[openai,anthropic]
python -c "import importlib.metadata as m; print(m.version('kazenai'), m.version('kazenai-finops'))"
python -c "from kazenai_finops import monitor, BudgetExceeded, StreamCutoffError; print('imports OK')"
```

The versions must be `1.1.1 1.1.1`. Run the packaged smoke test and the
supported synchronous OpenAI/Anthropic manager tests using mocked transports or
a non-production tenant.

## 6. Publish `kazenai-finops==1.1.1`

Prefer PyPI Trusted Publishing from a protected GitHub release workflow. If a
manual upload is unavoidable, use a narrowly scoped PyPI token from the clean
release environment:

```bash
python -m twine upload dist/*
```

Publishing is irreversible. Check the project name, version, commit SHA and
artifact hashes immediately before approval.

## 7. Verify both packages from public PyPI

After PyPI serves FinOps 1.1.1, create one more fresh environment:

```bash
python3 -m venv .venv-public
source .venv-public/bin/activate
python -m pip install --upgrade pip
python -m pip install --no-cache-dir "kazenai-finops[openai,anthropic]==1.1.1"
python -c "import importlib.metadata as m; print(m.version('kazenai'), m.version('kazenai-finops'))"
```

Rerun the clean-install smoke test for non-streaming calls, `stream=True`, the
official OpenAI and Anthropic stream managers, one pre-dispatch deny, and one
cancelled/error stream. Verify exactly one reservation/finalization lifecycle
per call and pending reconciliation rather than an exact-zero settlement when
authoritative usage is absent.

## 8. Tag and update downstream surfaces

- Tag the exact published commit as `v1.1.1`.
- Create a GitHub Release linked to the tested commit and record artifact hashes
  plus the CI run used as evidence.
- Update demo dependency pins only after both public packages pass the final
  clean-install smoke test.
- Deploy the documentation revision that describes those exact published
  versions.

See [PYPI_DRY_RUN.md](PYPI_DRY_RUN.md) for the release evidence checklist.
