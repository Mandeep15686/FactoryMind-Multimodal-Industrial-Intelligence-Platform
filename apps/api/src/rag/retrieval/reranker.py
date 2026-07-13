"""Cross-encoder re-ranking — delegates to the HF text-ranking task."""
from __future__ import annotations

from src.core.config import settings
from src.hf_tasks.text_ranking import rerank
from src.models.schemas import Document


def rerank_documents(query: str, docs: list[Document], top_k: int | None = None) -> list[Document]:
    """Re-rank the fused candidate set down to the highest-precision top_k."""
    return rerank(query, docs, top_k=top_k or settings.rerank_top_k)
