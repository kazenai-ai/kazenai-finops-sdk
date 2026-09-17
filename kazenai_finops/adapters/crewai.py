"""CrewAI adapter — re-export from kazenai-core for the canonical import path."""

from __future__ import annotations

try:
    from kazenai.integrations.crewai import wrap_crew_kickoff  # noqa: F401
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "kazenai-finops[crewai] requires `crewai` to be installed. "
        "Install it with: pip install kazenai-finops[crewai]"
    ) from exc

__all__ = ["wrap_crew_kickoff"]
