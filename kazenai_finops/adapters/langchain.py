"""LangChain adapter — re-export from kazenai-core for the canonical import path.

End users:
    from kazenai_finops.adapters.langchain import wrap_langchain_runnable
"""

from __future__ import annotations

try:
    from kazenai.integrations.langchain import (        # noqa: F401
        KazenCallbackHandler,
        wrap_langchain_runnable,
    )
except ImportError as exc:  # pragma: no cover — surfaced to user with actionable message
    raise ImportError(
        "kazenai-finops[langchain] requires `langchain-core` to be installed. "
        "Install it with: pip install kazenai-finops[langchain]"
    ) from exc

__all__ = ["KazenCallbackHandler", "wrap_langchain_runnable"]
