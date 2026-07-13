"""Dense retrieval — Qdrant HNSW with an in-memory cosine fallback."""
from __future__ import annotations

from src.core.config import settings
from src.hf_tasks.sentence_similarity import embed_texts, similarity
from src.models.schemas import Document
from src.rag._corpus import CORPUS


class DenseRetriever:
    """Vector search over knowledge chunks.

    Attempts a Qdrant connection; if unavailable, performs brute-force cosine
    similarity over the in-memory corpus (dev/offline mode).
    """

    def __init__(self) -> None:
        self._qdrant = None
        self._corpus: list[Document] = list(CORPUS)
        self._embeddings: list[list[float]] = []
        try:  # pragma: no cover - optional service
            from qdrant_client import QdrantClient

            self._qdrant = QdrantClient(url=settings.qdrant_url, timeout=2.0)
            self._qdrant.get_collections()
        except Exception:
            self._qdrant = None
            self._embeddings = embed_texts([d.text for d in self._corpus])

    def search(self, query: str, filters: dict | None = None, top_k: int | None = None) -> list[Document]:
        top_k = top_k or settings.retrieval_top_k
        if self._qdrant is not None:  # pragma: no cover
            try:
                qvec = embed_texts([query])[0]
                hits = self._qdrant.search(
                    collection_name=settings.qdrant_collection, query_vector=qvec, limit=top_k
                )
                return [
                    Document(
                        doc_id=str(h.id),
                        text=h.payload.get("text", ""),
                        score=float(h.score),
                        metadata=h.payload.get("metadata", {}),
                        source=h.payload.get("source"),
                    )
                    for h in hits
                ]
            except Exception:
                pass
        # ── in-memory fallback with metadata pre-filtering ──
        candidates = self._prefilter(filters)
        qvec = embed_texts([query])[0]
        scored: list[Document] = []
        for doc, emb in candidates:
            d = doc.model_copy()
            d.score = round(similarity(qvec, emb), 4)
            scored.append(d)
        scored.sort(key=lambda d: d.score, reverse=True)
        return scored[:top_k]

    def _prefilter(self, filters: dict | None) -> list[tuple[Document, list[float]]]:
        pairs = list(zip(self._corpus, self._embeddings))
        if not filters:
            return pairs
        out = []
        for doc, emb in pairs:
            ok = True
            for key, val in filters.items():
                mv = doc.metadata.get(key)
                if val and mv not in (val, "ANY") and mv != "ANY":
                    ok = False
                    break
            if ok:
                out.append((doc, emb))
        return out or pairs
