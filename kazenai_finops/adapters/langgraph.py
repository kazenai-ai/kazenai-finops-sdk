"""LangGraph adapter — thin re-export from kazenai-core."""

from __future__ import annotations

try:
    from kazenai.integrations.langgraph import (
        LangGraphAdapter,
        declare_langgraph_control_boundary,
        wrap_graph,
        wrap_graph_invoke,
    )
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "kazenai-finops[langgraph] requires the langgraph extra. "
        "Install it with: pip install kazenai-finops[langgraph]"
    ) from exc

__all__ = ["LangGraphAdapter", "declare_langgraph_control_boundary", "wrap_graph", "wrap_graph_invoke"]
