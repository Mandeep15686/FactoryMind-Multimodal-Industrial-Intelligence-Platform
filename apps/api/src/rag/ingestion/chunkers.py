"""Chunking strategies — semantic (embedding-distance) + recursive character."""
from __future__ import annotations

import re


def semantic_chunks(text: str, max_tokens: int = 256) -> list[str]:
    """Mock SemanticSplitter: group sentences, breaking on paragraph/topic gaps.

    A production implementation breaks where consecutive-sentence embedding
    cosine distance spikes; here we approximate with paragraph + length bounds.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    for para in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", para)
        buf: list[str] = []
        count = 0
        for s in sentences:
            n = len(s.split())
            if count + n > max_tokens and buf:
                chunks.append(" ".join(buf))
                buf, count = [], 0
            buf.append(s)
            count += n
        if buf:
            chunks.append(" ".join(buf))
    return chunks or ([text] if text.strip() else [])


def recursive_chunks(text: str, size: int = 2048, overlap: int = 200) -> list[str]:
    """RecursiveCharacterSplitter — fixed windows with overlap (token ≈ word)."""
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(size - overlap, 1)
    for start in range(0, len(words), step):
        window = words[start : start + size]
        if window:
            chunks.append(" ".join(window))
        if start + size >= len(words):
            break
    return chunks
