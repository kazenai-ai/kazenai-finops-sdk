"""Framework adapters for kazenai-finops.

Each adapter wraps a specific agent framework (LangChain, LangGraph,
CrewAI, AutoGen) so the user gets cost control + traces with a one-line
wrap. Importing a sub-module requires the corresponding extra:

    pip install kazenai-finops[langchain]
    pip install kazenai-finops[langgraph]
    pip install kazenai-finops[crewai]
    pip install kazenai-finops[autogen]
"""

from __future__ import annotations

__all__ = ["langchain", "langgraph", "crewai", "autogen"]
