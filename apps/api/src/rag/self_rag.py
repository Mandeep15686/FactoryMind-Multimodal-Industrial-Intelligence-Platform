"""Self-RAG quality gate — scores retrieved context on 4 dimensions.

If the mean score falls below ``settings.self_rag_threshold`` the retrieval
agent re-queries with an expanded query.
"""
from __future__ import annotations

from datetime import datetime

from src.models.schemas import Document


def _relevance(query: str, docs: list[Document]) -> float:
    if not docs:
        return 0.0
    q = set(query.lower().split())
    scores = []
    for d in docs:
        toks = set(d.text.lower().split())
        scores.append(len(q & toks) / (len(q) or 1))
    return min(1.0, sum(scores) / len(scores) * 2)


def _recency(docs: list[Document]) -> float:
    years = []
    for d in docs:
        date = str(d.metadata.get("date", ""))[:4]
        if date.isdigit():
            years.append(int(date))
    if not years:
        return 0.7
    newest = max(years)
    return max(0.3, min(1.0, 1.0 - (datetime.utcnow().year - newest) * 0.15))


def _completeness(docs: list[Document]) -> float:
    return min(1.0, len(docs) / 5.0)


def _specificity(docs: list[Document]) -> float:
    typed = sum(1 for d in docs if d.metadata.get("machine_type") not in (None, "ANY"))
    return typed / (len(docs) or 1)


def score_context(query: str, docs: list[Document]) -> float:
    """Return the mean of the four quality sub-scores (0..1)."""
    dims = [
        _relevance(query, docs),
        _recency(docs),
        _completeness(docs),
        _specificity(docs),
    ]
    return round(sum(dims) / len(dims), 4)
