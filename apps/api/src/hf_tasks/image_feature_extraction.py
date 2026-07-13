"""Image Feature Extraction — DINOv2-ViT-L/14. Dense visual embeddings."""
from __future__ import annotations

import math

from src.core.config import settings
from src.hf_tasks._client import fetch_bytes, hf_infer, is_mock, seeded_rng

MODEL = settings.visual_embedding_model  # facebook/dinov2-large


def extract_features(image_url: str) -> list[float]:
    """Return an L2-normalized embedding of length ``visual_embedding_dim``."""
    dim = settings.visual_embedding_dim
    if not is_mock():
        payload = fetch_bytes(image_url)
        if payload is not None:
            result = hf_infer(MODEL, payload, task="feature-extraction")
            if result:
                vec = result[0] if isinstance(result[0], list) else result
                return _normalize([float(x) for x in vec][:dim])
    rng = seeded_rng("vec:" + image_url)
    return _normalize([rng.gauss(0, 1) for _ in range(dim)])


def _normalize(v: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]
