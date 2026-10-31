"""Package metadata, provider extras, and re-export identity for 1.2.1."""

from __future__ import annotations

import re
from pathlib import Path

import kazenai
import kazenai_finops
from kazenai import monitor as core_monitor
from kazenai_finops import monitor as finops_monitor

_ROOT = Path(__file__).resolve().parents[1]
_EXPECTED = "1.2.1"
_OPENAI_BOUND = "openai>=1.40,<3"
_ANTHROPIC_BOUND = "anthropic>=0.39,<1"


def _pyproject_text() -> str:
    return (_ROOT / "pyproject.toml").read_text(encoding="utf-8")


def _optional_extra(name: str) -> list[str]:
    text = _pyproject_text()
    block = re.search(
        rf'(?ms)^{re.escape(name)}\s*=\s*\[(.*?)\]',
        text,
    )
    assert block is not None, f"missing optional-dependencies.{name}"
    return re.findall(r'"([^"]+)"', block.group(1))


def test_runtime_and_pyproject_version_match_expected() -> None:
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', _pyproject_text())
    assert match is not None
    assert match.group(1) == _EXPECTED
    assert kazenai_finops.__version__ == _EXPECTED


def test_depends_on_core_1_2_range() -> None:
    text = _pyproject_text()
    # [server] carries cryptography, needed to verify the signed live price catalog.
    assert '"kazenai[server]>=1.2.1,<2.0"' in text
    assert '"kazen-event-schema>=0.6.6,<0.7"' in text


def test_optional_provider_extras_use_supported_bounds() -> None:
    assert _optional_extra("openai") == [_OPENAI_BOUND]
    assert _optional_extra("anthropic") == [_ANTHROPIC_BOUND]
    assert _optional_extra("providers") == [_OPENAI_BOUND, _ANTHROPIC_BOUND]


def test_finops_monitor_is_core_monitor_identity() -> None:
    assert finops_monitor is core_monitor
    assert kazenai_finops.monitor is kazenai.monitor


def test_attribution_api_is_reexported_from_core() -> None:
    # The README imports these from kazenai_finops (1.2.1).
    for name in ("use_attribution", "AttributionConflict", "AttributionContext", "CustomerIdRequired"):
        assert name in kazenai_finops.__all__
        assert getattr(kazenai_finops, name) is getattr(kazenai, name)


def test_active_first_run_docs_prefer_bounded_extras() -> None:
    text = (_ROOT / "README.md").read_text(encoding="utf-8")
    assert f"kazenai-finops[openai]=={_EXPECTED}" in text
    assert not re.search(
        r'pip install(?:\s+"?)kazenai-finops(?!\[[^\]]+\])(?:"?==[0-9.]+)?\s+"?(?:openai|anthropic)\b',
        text,
    )


_SUPPORTED_PYTHONS = ["3.10", "3.11", "3.12", "3.13", "3.14"]


def _ci_matrix_pythons() -> list[str]:
    text = (_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    matrices = re.findall(r"(?m)^\s*python-version:\s*\[([^\]]*)\]", text)
    assert len(matrices) == 1, "expected exactly one python-version test matrix in ci.yml"
    return re.findall(r'"(3\.\d+)"', matrices[0])


def test_python_classifiers_match_the_ci_matrix_and_readme() -> None:
    # The package claims only the Python versions CI tests (3.13 and 3.14 since 1.2.1).
    classifiers = re.findall(r'"Programming Language :: Python :: (3\.\d+)"', _pyproject_text())
    assert classifiers == _ci_matrix_pythons() == _SUPPORTED_PYTHONS
    assert re.search(r'(?m)^requires-python\s*=\s*">=3\.10"', _pyproject_text())
    readme = (_ROOT / "README.md").read_text(encoding="utf-8")
    assert f"Requires Python {_SUPPORTED_PYTHONS[0]}–{_SUPPORTED_PYTHONS[-1]}." in readme
