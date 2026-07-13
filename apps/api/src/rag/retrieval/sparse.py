"""Sparse retrieval — BM25 with a domain tokenizer that keeps part codes whole.

Pure-Python BM25 (no Elasticsearch dependency required) over the in-memory
corpus. In production this is backed by an OpenSearch/Elasticsearch index.
"""
from __future__ import annotations

import math
import re
from collections import Counter

from src.core.config import settings
from src.models.schemas import Document
from src.rag._corpus import CORPUS

# Keep alphanumeric part/error codes (SKF-22222-E-C3, E-204) as single tokens.
_CODE = re.compile(r"[A-Z]{2,}-\d+(?:-[A-Z0-9]+)*|E-?\d{2,4}", re.I)
_WORD = re.compile(r"[a-z0-9]+", re.I)


def tokenize(text: str) -> list[str]:
    codes = _CODE.findall(text)
    scrubbed = _CODE.sub(" ", text)
    words = [w.lower() for w in _WORD.findall(scrubbed)]
    return [c.lower() for c in codes] + words


class SparseRetriever:
    """BM25 ranking over the corpus."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self._docs: list[Document] = list(CORPUS)
        self._tokenized = [tokenize(d.text) for d in self._docs]
        self._doc_len = [len(t) for t in self._tokenized]
        self._avgdl = (sum(self._doc_len) / len(self._doc_len)) if self._doc_len else 0.0
        self._df: Counter[str] = Counter()
        for toks in self._tokenized:
            for term in set(toks):
                self._df[term] += 1
        self._N = len(self._docs)

    def _idf(self, term: str) -> float:
        n = self._df.get(term, 0)
        return math.log(1 + (self._N - n + 0.5) / (n + 0.5))

    def search(self, query: str, top_k: int | None = None) -> list[Document]:
        top_k = top_k or settings.retrieval_top_k
        q_terms = tokenize(query)
        scored: list[Document] = []
        for doc, toks, dl in zip(self._docs, self._tokenized, self._doc_len):
            tf = Counter(toks)
            score = 0.0
            for term in q_terms:
                if term not in tf:
                    continue
                idf = self._idf(term)
                num = tf[term] * (self.k1 + 1)
                den = tf[term] + self.k1 * (1 - self.b + self.b * dl / (self._avgdl or 1))
                score += idf * num / den
            d = doc.model_copy()
            d.score = round(score, 4)
            scored.append(d)
        scored.sort(key=lambda d: d.score, reverse=True)
        return [d for d in scored if d.score > 0][:top_k]
