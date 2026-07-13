"""Summarization — BART-large-CNN / LLaMA-3-8B. Shift report drafting."""
from __future__ import annotations

from src.hf_tasks._client import hf_infer, is_mock

MODEL = "facebook/bart-large-cnn"


def summarize(text: str, max_words: int = 400) -> str:
    """Condense event-log text into a bounded summary."""
    if not is_mock():
        result = hf_infer(
            MODEL,
            {"inputs": text, "parameters": {"max_length": max_words, "min_length": 60}},
            task="summarization",
        )
        if result:
            return result[0].get("summary_text", "") if isinstance(result, list) else str(result)
    # ── extractive mock: keep the most information-dense sentences ──
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    if not sentences:
        return "No significant events recorded this shift."
    scored = sorted(sentences, key=lambda s: len(s.split()), reverse=True)
    kept: list[str] = []
    words = 0
    for s in scored:
        w = len(s.split())
        if words + w > max_words:
            break
        kept.append(s)
        words += w
    # restore original ordering
    kept_set = set(kept)
    ordered = [s for s in sentences if s in kept_set]
    return ". ".join(ordered) + "."
