"""Sentence Similarity — BGE-M3 / E5-large. Dense retrieval embeddings."""
from __future__ import annotations

import hashlib
import math

from src.core.config import settings
from src.hf_tasks._client import hf_infer, is_mock

MODEL = settings.text_embedding_model  # BAAI/bge-m3


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Return one L2-normalized embedding per input text."""
    dim = settings.text_embedding_dim
    if not is_mock():
        result = hf_infer(
            MODEL,
            {"inputs": {"source_sentence": texts[0], "sentences": texts}},
            task="feature-extraction",
        )
        if result and isinstance(result[0], list):
            return [_normalize([float(x) for x in v][:dim]) for v in result]
    return [_hash_embed(t, dim) for t in texts]


def similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity of two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def _hash_embed(text: str, dim: int) -> list[float]:
    """Deterministic bag-of-hashed-tokens embedding — stable across runs."""
    vec = [0.0] * dim
    for tok in text.lower().split():
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        vec[h % dim] += 1.0
        vec[(h // dim) % dim] += 0.5
    return _normalize(vec)


def _normalize(v: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]
