# Vendored wheels (CI)

`kazenai` and `kazen-event-schema` are not published at the workspace versions
yet. CI installs these pinned wheels before `pip install -e ".[dev]"`.
Install `kazen_event_schema` first — the `kazenai` wheel depends on it.

| Wheel | Purpose |
|-------|---------|
| `kazen_event_schema-0.6.0-py3-none-any.whl` | Satisfies `kazen-event-schema>=0.6.0,<0.7` |
| `kazenai-1.0.1-py3-none-any.whl` | Satisfies `kazenai>=1.0.1,<2.0` |

Refresh:
```bash
cd ../kazenai-core && python -m build
cp dist/kazenai-1.0.1-py3-none-any.whl ../kazenai-finops-sdk/vendor/
cd ../kazen-event-schema && python -m build
cp dist/kazen_event_schema-0.6.0-py3-none-any.whl ../kazenai-finops-sdk/vendor/
```
