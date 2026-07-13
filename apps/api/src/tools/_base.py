"""Shared helpers for LangChain tool wrappers.

Provides a ``tool`` decorator that degrades to a no-op when langchain_core is
absent, so the plain callables remain importable in minimal environments.
"""
from __future__ import annotations

from typing import Callable

try:  # pragma: no cover - optional dep
    from langchain_core.tools import tool as _lc_tool

    def tool(fn: Callable) -> Callable:  # type: ignore[misc]
        return _lc_tool(fn)
except Exception:  # pragma: no cover

    def tool(fn: Callable) -> Callable:
        fn.is_tool = True  # type: ignore[attr-defined]
        return fn
