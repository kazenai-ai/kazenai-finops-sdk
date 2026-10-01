# Vendored wheels

The current CI installs the reviewed schema wheel from this directory, then
resolves `kazenai>=1.1.0,<2.0` through the package dependency. This deliberately
proves that the required Core release is available independently of a sibling
checkout.

| Wheel | Purpose |
|-------|---------|
| `kazen_event_schema-0.6.3-py3-none-any.whl` | Reviewed schema input used by CI |
| `kazenai-1.0.5-py3-none-any.whl` | Legacy artifact; not used by the 1.1.0 CI or release path |

Do not install the legacy Core wheel while certifying or releasing
`kazenai-finops==1.1.0`. The release requires public `kazenai==1.1.0` first.

Refresh the reviewed schema wheel only when the dependency range and CI input
are intentionally changed:

```bash
python -m pip download --no-deps -d vendor/ kazen-event-schema==0.6.3

# Or build the reviewed schema source locally:
cd ../kazen-event-schema && python -m build
cp dist/kazen_event_schema-*-py3-none-any.whl ../kazenai-finops-sdk/vendor/
```

After replacement, record the wheel hash in the review and rerun the full CI
matrix.
