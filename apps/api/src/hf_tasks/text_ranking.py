"""Text Ranking — cross-encoder/ms-marco-MiniLM. Re-ranks RAG candidates."""
from __future__ import annotations

from src.core.config import settings
from src.hf_tasks._client import hf_infer, is_mock
from src.models.schemas import Document

MODEL = settings.reranker_model


def rerank(query: str, docs: list[Document], top_k: int = 5) -> list[Document]:
    """Jointly score (query, doc) pairs and return the top_k documents."""
    if not docs:
        return []
    if not is_mock():
        result = hf_infer(
            MODEL,
            {"inputs": {"source_sentence": query, "sentences": [d.text for d in docs]}},
            task="sentence-similarity",
        )
        if result:
            for d, score in zip(docs, result):
                d.score = float(score)
            return sorted(docs, key=lambda d: d.score, reverse=True)[:top_k]
    q_tokens = set(query.lower().split())
    for d in docs:
        d_tokens = d.text.lower().split()
        if not d_tokens:
            d.score = 0.0
            continue
        overlap = sum(1 for t in d_tokens if t in q_tokens)
        d.score = round(overlap / (len(d_tokens) ** 0.5), 4)
    return sorted(docs, key=lambda d: d.score, reverse=True)[:top_k]
