# Releasing kazenai-finops

This is the **customer-facing** package — every release is visible on
PyPI. Treat it like a public API.

---

## 0. Pre-flight

1. `git status --short` is empty.
2. Local kazenai-core is at a tagged version matching the dependency pin in
   `pyproject.toml`.
3. `kazen-event-schema` version pin is up-to-date.
4. README.md examples have been hand-run against the new version.

---

## 1. Run tests

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e . -e ../kazenai-core -e ../kazen-event-schema
pip install -r <(echo "pytest>=8.0"; echo "pytest-cov>=5.0")
pytest tests/ -v
```

All must pass. Adapter tests run without extras installed (they
verify the actionable-error message path).

---

## 2. Bump the version

Update **both**:

```
kazenai_finops/__init__.py  # __version__ = "X.Y.Z"
pyproject.toml              # version = "X.Y.Z"
```

Use SemVer. The first major bump (1.0.0) commits to the public API
shape and triggers a deprecation policy.

---

## 3. Build + test the wheel

```bash
rm -rf dist build *.egg-info
python -m build
twine check dist/*
```

---

## 4. Publish to test PyPI first

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ --no-deps kazenai-finops
# Smoke-test in a fresh venv:
python -c "from kazenai_finops import monitor, KazenBudgetExceeded; print('OK')"
```

---

## 5. Publish to real PyPI

```bash
twine upload dist/*
```

---

## 6. Tag + push

```bash
git tag -a kazenai-finops-vX.Y.Z -m "kazenai-finops vX.Y.Z"
git push --tags
```

---

## 7. Post-release

* Update the public README at https://kazenai.com.
* Update the onboarding wizard snippet (Step 3) to reference the new
  version if any API changed.
* Post a LinkedIn announcement (see v3 plan §7 schedule).
* Open a GitHub release with the changelog from `git log v(N-1)..vN`.

---

## Anti-patterns

* Publishing without testing in a fresh venv first.
* Bumping the version in only one of the two files.
* Releasing without updating the README install command.
* Force-publishing a yanked version under the same number (PyPI rejects this).
* Breaking the `monitor()` signature in a minor bump.
