"""Context compression — LLMLingua-2 style information-density pruning.

Removes low-information sentences while preserving technical entities (part
codes, error codes, torque specs) to cut LLM input tokens without losing
grounding signal.
"""
from __future__ import annotations

import re

from src.models.schemas import Document

_ENTITY = re.compile(r"[A-Z]{2,}-\d+|E-?\d{2,4}|\d+\s?(?:Nm|C|kHz|Hz|mm|micron)", re.I)
_STOP = {"the", "a", "an", "of", "to", "and", "is", "are", "in", "on", "for", "with", "as", "it"}


def _sentence_score(sentence: str) -> float:
    tokens = sentence.split()
    if not tokens:
        return 0.0
    content = [t for t in tokens if t.lower() not in _STOP]
    entity_bonus = 2.0 * len(_ENTITY.findall(sentence))
    return (len(content) / len(tokens)) + entity_bonus


def compress(docs: list[Document], ratio: float = 0.5) -> list[Document]:
    """Compress each document to roughly ``ratio`` of its sentences."""
    out: list[Document] = []
    for doc in docs:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", doc.text) if s.strip()]
        if len(sentences) <= 2:
            out.append(doc)
            continue
        keep_n = max(1, int(len(sentences) * ratio))
        ranked = sorted(range(len(sentences)), key=lambda i: _sentence_score(sentences[i]), reverse=True)
        keep_idx = sorted(ranked[:keep_n])
        compressed = " ".join(sentences[i] for i in keep_idx)
        d = doc.model_copy()
        d.text = compressed
        d.metadata = {**doc.metadata, "compressed": True, "orig_sentences": len(sentences)}
        out.append(d)
    return out
