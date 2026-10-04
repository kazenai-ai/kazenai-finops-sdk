"""Smoke tests for the kazenai-finops wrapper package.

These tests verify:
    * Top-level imports work without optional extras installed.
    * Runtime ``__version__`` agrees with ``pyproject.toml`` and, when
      installed, with distribution metadata.
    * Re-exported symbols come from kazenai-core (not duplicated locally).
    * Adapter sub-modules raise actionable ImportError when their extra
      is missing (no silent failure).
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

_EXPECTED_RELEASE = "1.1.1"
_PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _pyproject_version() -> str:
    text = _PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', text)
    assert match is not None, "pyproject.toml must declare version"
    return match.group(1)


def test_top_level_imports_without_extras():
    import kazenai_finops as kf

    assert kf.__version__ == _EXPECTED_RELEASE
    from kazenai.enforcement import BudgetExceeded as CoreBudgetExceeded

    assert kf.BudgetExceeded is CoreBudgetExceeded
    from kazenai import UnknownModelError as CoreUnknownModelError

    assert kf.UnknownModelError is CoreUnknownModelError
    assert callable(kf.monitor)
    assert kf.KazenBudgetExceeded is kf.KazenCircuitBreaker
    # KazenEvent is the canonical schema, not a local duplicate.
    from kazenai.schema import KazenEvent as CoreKazenEvent

    assert kf.KazenEvent is CoreKazenEvent


def test_version_authority_matches_pyproject():
    import kazenai_finops as kf

    py_version = _pyproject_version()
    assert py_version == _EXPECTED_RELEASE
    assert kf.__version__ == py_version


def test_installed_distribution_version_when_available():
    from importlib.metadata import PackageNotFoundError, version

    import kazenai_finops as kf

    try:
        dist_version = version("kazenai-finops")
    except PackageNotFoundError:
        pytest.skip("kazenai-finops distribution metadata not installed")
    assert dist_version == _EXPECTED_RELEASE
    assert kf.__version__ == dist_version


def test_project_urls_point_at_canonical_public_surfaces():
    text = _PYPROJECT.read_text(encoding="utf-8")
    block = re.search(r"(?ms)^\[project\.urls\]\n(.*?)(?:\n\[|\Z)", text)
    assert block is not None
    body = block.group(1)
    assert 'Repository = "https://github.com/kazenai-ai/kazenai-finops-sdk"' in body
    assert 'Documentation = "https://docs.kazenai.com/"' in body
    assert 'Changelog = "https://github.com/kazenai-ai/kazenai-finops-sdk/releases"' in body
    assert '"Bug Tracker" = "https://github.com/kazenai-ai/kazenai-finops-sdk/issues"' in body
    assert "github.com/KazenAI/" not in body


def test_adapters_subpackage_importable():
    from kazenai_finops import adapters

    # The sub-package itself imports cleanly even when no extras installed.
    assert hasattr(adapters, "__all__")


@pytest.mark.parametrize("adapter_name", ["langchain", "langgraph", "crewai"])
def test_adapter_raises_actionable_error_when_extra_missing(adapter_name, monkeypatch):
    """If the framework dep isn't installed, the import error message
    must tell the user exactly which `pip install` command to run."""
    # Force the underlying kazenai-core import to fail.
    monkeypatch.setitem(
        importlib.sys.modules,
        f"kazenai.integrations.{adapter_name}",
        None,
    )
    with pytest.raises(ImportError) as exc_info:
        importlib.import_module(f"kazenai_finops.adapters.{adapter_name}")
    msg = str(exc_info.value)
    assert "pip install" in msg
    assert adapter_name in msg


def test_version_string_matches_init():
    import kazenai_finops

    assert isinstance(kazenai_finops.__version__, str)
    assert kazenai_finops.__version__.count(".") == 2
    assert kazenai_finops.__version__ == _EXPECTED_RELEASE
