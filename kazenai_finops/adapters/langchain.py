"""LangChain adapter — thin re-export from kazenai-core."""

from __future__ import annotations

try:
    from kazenai.integrations.langchain import (
        KazenCallbackHandler,
        LangChainRunnableAdapter,
        bind_monitored_chat_anthropic,
        bind_monitored_chat_openai,
        bound_guarded_client,
        declare_langchain_control_boundary,
        wrap_langchain_runnable,
        wrap_model_call_middleware,
    )
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "kazenai-finops[langchain] requires the langchain extra. "
        "Install it with: pip install kazenai-finops[langchain]"
    ) from exc

__all__ = [
    "KazenCallbackHandler",
    "LangChainRunnableAdapter",
    "bind_monitored_chat_anthropic",
    "bind_monitored_chat_openai",
    "bound_guarded_client",
    "declare_langchain_control_boundary",
    "wrap_langchain_runnable",
    "wrap_model_call_middleware",
]
