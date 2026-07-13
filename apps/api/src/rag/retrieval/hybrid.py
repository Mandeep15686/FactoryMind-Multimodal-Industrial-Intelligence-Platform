"""Hybrid search fusion — Reciprocal Rank Fusion (RRF)."""
from __future__ import annotations

from src.core.config import settings
from src.models.schemas import Document


def reciprocal_rank_fusion(rankings: list[list[Document]], k: int | None = None) -> list[Document]:
    """Merge multiple ranked lists via RRF: score = Σ 1/(k + rank_i).

    RRF is scale-free, so it fuses dense (cosine) and sparse (BM25) rankings that
    have incompatible score ranges.
    """
    k = k or settings.rrf_k
    fused: dict[str, float] = {}
    best_doc: dict[str, Document] = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking):
            fused[doc.doc_id] = fused.get(doc.doc_id, 0.0) + 1.0 / (k + rank + 1)
            if doc.doc_id not in best_doc:
                best_doc[doc.doc_id] = doc
    out: list[Document] = []
    for doc_id, score in sorted(fused.items(), key=lambda kv: kv[1], reverse=True):
        d = best_doc[doc_id].model_copy()
        d.score = round(score, 5)
        out.append(d)
    return out
