"""Embedding helpers wrapping the HF sentence-similarity + visual models."""
from __future__ import annotations

from src.hf_tasks.image_feature_extraction import extract_features
from src.hf_tasks.sentence_similarity import embed_texts
from src.models.schemas import Document


def embed_text_docs(docs: list[Document]) -> list[list[float]]:
    """Embed the text of each document with BGE-M3 (or mock)."""
    if not docs:
        return []
    return embed_texts([d.text for d in docs])


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]


def embed_visual(image_url: str) -> list[float]:
    """DINOv2 visual embedding for defect similarity search."""
    return extract_features(image_url)
