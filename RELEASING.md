# Releasing `kazenai-finops`

`kazenai-finops` is the customer SDK. It re-exports `kazenai` and is released at
the same version, after `kazenai` is on PyPI. Replace `X.Y.Z` with the release
version.

## 1. Confirm `kazenai` X.Y.Z is public

```bash
python3 -m venv /tmp/kazenai-finops-prereq
/tmp/kazenai-finops-prereq/bin/pip install --no-cache-dir "kazenai==X.Y.Z"
```

## 2. Prepare the release commit

- Set `X.Y.Z` in `pyproject.toml` and `kazenai_finops/__init__.py`, and require
  `kazenai>=X.Y.Z,<2.0`.
- Update the install commands in the README and add `RELEASE_NOTES_X.Y.Z.md`.
- Make sure the commit contains no secrets, customer data, local environments
  or generated files, then push it to `main`.

## 3. Wait for CI

CI installs `kazenai` from PyPI and must pass on Python 3.10, 3.11 and 3.12.

## 4. Tag and publish

```bash
git tag -a vX.Y.Z -m "kazenai-finops X.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z --title "kazenai-finops X.Y.Z" --notes-file RELEASE_NOTES_X.Y.Z.md --verify-tag
```

The tag runs the publish workflow (PyPI Trusted Publishing).

## 5. Verify from PyPI

```bash
python3 -m venv /tmp/kazenai-finops-check
/tmp/kazenai-finops-check/bin/pip install --no-cache-dir "kazenai-finops[openai,anthropic]==X.Y.Z"
/tmp/kazenai-finops-check/bin/python -c "import importlib.metadata as m; print(m.version('kazenai'), m.version('kazenai-finops'))"
```

Both versions must print `X.Y.Z`.
