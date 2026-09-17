# PyPI release dry-run — 2026-06-10

Packages prepared for **1.0.1** (core/finops) and **0.6.0** (schema).  
Real upload pending your approval after reviewing this file.

## twine check (all PASSED)

```
kazen-event-schema/dist/kazen_event_schema-0.6.0-py3-none-any.whl: PASSED
kazen-event-schema/dist/kazen_event_schema-0.6.0.tar.gz: PASSED
kazenai-core/dist/kazenai-1.0.1-py3-none-any.whl: PASSED
kazenai-core/dist/kazenai-1.0.1.tar.gz: PASSED
kazenai-finops-sdk/dist/kazenai_finops-1.0.1-py3-none-any.whl: PASSED
kazenai-finops-sdk/dist/kazenai_finops-1.0.1.tar.gz: PASSED
```

## Upload commands (run in order after approval)

```bash
# 1. schema
cd kazen-event-schema
twine upload dist/kazen_event_schema-0.6.0*

# 2. core
cd ../kazenai-core
twine upload dist/kazenai-1.0.1*

# 3. finops-sdk (customer-facing)
cd ../kazenai-finops-sdk
twine upload dist/kazenai_finops-1.0.1*
```

## Tags

```bash
git tag -a schema/v0.6.0 -m "kazen-event-schema v0.6.0"   # in kazen-event-schema repo
git tag -a core/v1.0.1 -m "kazenai v1.0.1"               # in kazenai-core repo
git tag -a sdk/v1.0.1 -m "kazenai-finops v1.0.1"         # in kazenai-finops-sdk repo
git push --tags
```

## Test PyPI (optional smoke)

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ kazenai-finops==1.0.1
python -c "from kazenai_finops import monitor, KazenBudgetExceeded, BudgetExceeded; print('OK')"
```

## What changed in 1.0.1

- `monitor()` auto-detects Anthropic clients (`patch_anthropic`)
- `timeline_path` / `KAZENAI_TIMELINE_PATH` exports FinOps JSONL timeline
- `BudgetExceeded` re-exported from `kazenai_finops`
- Dependency pins: `kazen-event-schema>=0.6.0,<0.7`
