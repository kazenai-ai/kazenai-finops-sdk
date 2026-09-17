"""LangGraph adapter — re-export from kazenai-core for the canonical import path."""

from __future__ import annotations

try:
    from kazenai.integrations.langgraph import wrap_graph_invoke  # noqa: F401
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "kazenai-finops[langgraph] requires `langgraph` to be installed. "
        "Install it with: pip install kazenai-finops[langgraph]"
    ) from exc

__all__ = ["wrap_graph_invoke"]
