"""Smoke tests for the kazenai-finops wrapper package.

These tests verify:
    * Top-level imports work without optional extras installed.
    * ``__version__`` matches pyproject.
    * Re-exported symbols come from kazenai-core (not duplicated locally).
    * Adapter sub-modules raise actionable ImportError when their extra
      is missing (no silent failure).
"""

from __future__ import annotations

import importlib

import pytest


def test_top_level_imports_without_extras():
    import kazenai_finops as kf
    assert kf.__version__ == "1.0.1"
    from kazenai.enforcement import BudgetExceeded as CoreBudgetExceeded
    assert kf.BudgetExceeded is CoreBudgetExceeded
    assert callable(kf.monitor)
    assert kf.KazenBudgetExceeded is kf.KazenCircuitBreaker
    # KazenEvent is the canonical schema, not a local duplicate.
    from kazenai.schema import KazenEvent as CoreKazenEvent
    assert kf.KazenEvent is CoreKazenEvent


def test_adapters_subpackage_importable():
    import kazenai_finops.adapters as adapters
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
