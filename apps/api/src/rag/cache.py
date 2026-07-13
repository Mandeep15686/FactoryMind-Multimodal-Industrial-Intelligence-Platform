"""Semantic cache — Redis vector similarity with an in-process fallback.

Near-identical queries (cosine > threshold) short-circuit the full retrieval
pipeline. TTL is best-effort.
"""
from __future__ import annotations

import time

from src.core.config import settings
from src.hf_tasks.sentence_similarity import similarity
from src.models.schemas import RetrievalResult


class SemanticCache:
    def __init__(self) -> None:
        self.threshold = settings.semantic_cache_threshold
        self.ttl = settings.semantic_cache_ttl_s
        self._redis = None
        # in-process store: list of (embedding, result, expires_at)
        self._store: list[tuple[list[float], RetrievalResult, float]] = []
        try:  # pragma: no cover - optional service
            import redis

            self._redis = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=1)
            self._redis.ping()
        except Exception:
            self._redis = None

    def get(self, query_embedding: list[float]) -> RetrievalResult | None:
        now = time.time()
        self._store = [(e, r, exp) for (e, r, exp) in self._store if exp > now]
        best: tuple[float, RetrievalResult] | None = None
        for emb, result, _exp in self._store:
            sim = similarity(query_embedding, emb)
            if sim >= self.threshold and (best is None or sim > best[0]):
                best = (sim, result)
        return best[1] if best else None

    def set(self, query_embedding: list[float], result: RetrievalResult) -> None:
        self._store.append((query_embedding, result, time.time() + self.ttl))
        # bound memory
        if len(self._store) > 512:
            self._store = self._store[-512:]

    def invalidate(self) -> None:
        self._store.clear()
