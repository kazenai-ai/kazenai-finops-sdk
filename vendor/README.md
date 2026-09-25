# Vendored wheels (CI)

Pinned wheels for hermetic CI. **`kazenai` and `kazen-event-schema` are on PyPI**;
keep vendor copies when CI must not reach the network or must pin exact files.
Install `kazen_event_schema` first — the `kazenai` wheel depends on it.

| Wheel | Purpose |
|-------|---------|
| `kazen_event_schema-0.6.1-py3-none-any.whl` | Prefer `pip install kazen-event-schema` for latest |
| `kazenai-1.0.2-py3-none-any.whl` | Prefer `pip install kazenai` for latest |

Refresh:
```bash
pip download --no-deps -d vendor/ kazen-event-schema==0.6.1 kazenai==1.0.2
# or build locally:
cd ../kazenai-core && python -m build
cp dist/kazenai-*-py3-none-any.whl ../kazenai-finops-sdk/vendor/
cd ../kazen-event-schema && python -m build
cp dist/kazen_event_schema-*-py3-none-any.whl ../kazenai-finops-sdk/vendor/
```
