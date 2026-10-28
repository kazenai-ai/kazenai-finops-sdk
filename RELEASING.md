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
- Update the install commands in the README and add a section at the top of `CHANGELOG.md` headed `## X.Y.Z - YYYY-MM-DD` (the release date).
- Make sure the commit contains no secrets, customer data, local environments
  or generated files, then push it to `main`.

## 3. Wait for CI

CI installs `kazenai` from PyPI and must pass on Python 3.10, 3.11 and 3.12.

## 4. Tag and publish

```bash
git tag -a vX.Y.Z -m "kazenai-finops X.Y.Z"
git push origin vX.Y.Z
# The Release body is this version's CHANGELOG.md section plus a docs and support line.
awk '/^## /{p=0} /^## X.Y.Z /{p=1; next} p' CHANGELOG.md > /tmp/notes-X.Y.Z.md
printf '\nDocs: https://docs.kazenai.com/ · Support: open an issue at https://github.com/kazenai-ai/kazenai-finops-sdk/issues\n' >> /tmp/notes-X.Y.Z.md
gh release create vX.Y.Z --title "kazenai-finops X.Y.Z" --notes-file /tmp/notes-X.Y.Z.md --verify-tag
```

The tag runs the publish workflow (PyPI Trusted Publishing).

## 5. Verify from PyPI

```bash
python3 -m venv /tmp/kazenai-finops-check
/tmp/kazenai-finops-check/bin/pip install --no-cache-dir "kazenai-finops[openai,anthropic]==X.Y.Z"
/tmp/kazenai-finops-check/bin/python -c "import importlib.metadata as m; print(m.version('kazenai'), m.version('kazenai-finops'))"
```

Both versions must print `X.Y.Z`.
