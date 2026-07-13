"""Shared HuggingFace Inference API client with a deterministic mock mode.

When ``settings.hf_use_mock`` is True (dev default) or no token is set, callers
use their own mock branch. Otherwise ``hf_infer`` POSTs to the HF endpoint.
"""
from __future__ import annotations

import hashlib
import random
from typing import Any

from src.core.config import settings


class MockOnly(Exception):
    """Raised internally to signal a caller should use its mock path."""


def is_mock() -> bool:
    return settings.hf_use_mock or not settings.hf_api_token


def seeded_rng(key: str) -> random.Random:
    """Deterministic RNG seeded by an input string — stable mocks per input."""
    digest = hashlib.sha256(key.encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def hf_infer(model: str, payload: dict | bytes, task: str = "") -> Any:
    """Call the HF Inference API. Returns None in mock mode."""
    if is_mock():
        return None
    import httpx  # local import keeps httpx optional for offline installs

    url = f"{settings.hf_inference_endpoint}/{model}"
    headers = {"Authorization": f"Bearer {settings.hf_api_token}"}
    try:
        if isinstance(payload, (bytes, bytearray)):
            resp = httpx.post(url, headers=headers, content=payload, timeout=30)
        else:
            resp = httpx.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        # Any network/model error → let caller fall back to mock.
        return None


def fetch_bytes(url: str) -> bytes | None:
    """Best-effort fetch of image/audio bytes for real inference."""
    if is_mock():
        return None
    try:
        import httpx

        resp = httpx.get(url, timeout=15)
        resp.raise_for_status()
        return resp.content
    except Exception:
        return None
