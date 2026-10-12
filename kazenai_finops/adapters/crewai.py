"""CrewAI adapter — thin re-export from kazenai-core."""

from __future__ import annotations

try:
    from kazenai.integrations.crewai import (
        CrewAdapter,
        KazenCrewListener,
        bind_crew_llm_client,
        wrap_crew,
        wrap_crew_kickoff,
    )
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "kazenai-finops[crewai] requires the crewai extra. "
        "Install it with: pip install kazenai-finops[crewai]"
    ) from exc

__all__ = [
    "CrewAdapter",
    "KazenCrewListener",
    "bind_crew_llm_client",
    "wrap_crew",
    "wrap_crew_kickoff",
]
