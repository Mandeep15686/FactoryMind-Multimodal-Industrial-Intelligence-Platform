"""End-to-end RAG orchestration (blueprint Section 8, 13 steps)."""
from __future__ import annotations

import logging

from src.core.config import settings
from src.hf_tasks.sentence_similarity import embed_texts
from src.models.schemas import Document, RetrievalResult
from src.rag._corpus import CORPUS
from src.rag.cache import SemanticCache
from src.rag.compression import compress
from src.rag.retrieval.dense import DenseRetriever
from src.rag.retrieval.graph import GraphRetriever
from src.rag.retrieval.hybrid import reciprocal_rank_fusion
from src.rag.retrieval.multi_query import generate_variants
from src.rag.retrieval.reranker import rerank_documents
from src.rag.retrieval.sparse import SparseRetriever
from src.rag.self_rag import score_context

logger = logging.getLogger("factorymind.rag")

# Instantiate retrievers once (they lazily connect / fall back to in-memory).
_dense = DenseRetriever()
_sparse = SparseRetriever()
_graph = GraphRetriever()
_cache = SemanticCache()


def retrieve_knowledge(
    query: str, machine_type: str | None = None, plant_id: str | None = None
) -> RetrievalResult:
    """Run the full hybrid Graph-RAG pipeline and return the top-k context."""
    q_embed = embed_texts([query])[0]

    # (12) semantic cache
    cached = _cache.get(q_embed)
    if cached is not None:
        logger.info("semantic cache hit")
        return cached

    filters = {"machine_type": machine_type} if machine_type else None

    # (6) multi-query expansion
    variants = generate_variants(query)

    # (4)(5) dense + sparse per variant
    rankings: list[list[Document]] = []
    for v in variants:
        rankings.append(_dense.search(v, filters=filters))
        rankings.append(_sparse.search(v))

    # (7) RRF fusion
    fused = reciprocal_rank_fusion(rankings)[: settings.retrieval_top_k]

    # (8) graph traversal for multi-hop context
    symptoms = [w for w in query.lower().split() if len(w) > 4]
    graph_paths = _graph.traverse(machine_type, symptoms)

    # (10) cross-encoder rerank → top-5
    reranked = rerank_documents(query, fused, top_k=settings.rerank_top_k)

    # (11) context compression
    compressed = compress(reranked, ratio=0.5)

    # (9) Self-RAG quality gate → re-retrieve once if weak
    score = score_context(query, compressed)
    if score < settings.self_rag_threshold:
        logger.info("self-rag re-retrieval (score=%.3f)", score)
        expanded = f"{query} failure mode root cause corrective action maintenance"
        more = reciprocal_rank_fusion(
            [_dense.search(expanded, filters=None), _sparse.search(expanded)]
        )[: settings.retrieval_top_k]
        reranked = rerank_documents(expanded, more, top_k=settings.rerank_top_k)
        compressed = compress(reranked, ratio=0.5)
        score = max(score, score_context(expanded, compressed))

    result = RetrievalResult(
        documents=compressed,
        retrieval_score=score,
        query_variants=variants,
        graph_paths=graph_paths,
    )

    _cache.set(q_embed, result)
    return result


def ingest_document(text_or_path: str, metadata: dict | None = None) -> int:
    """Ingest a document into the corpus (and stores when available).

    Returns the number of chunks added. In dev this appends to the in-memory
    corpus; in production it upserts to Qdrant + BM25 and updates Neo4j.
    """
    from src.rag.ingestion.chunkers import semantic_chunks

    chunks = semantic_chunks(text_or_path)
    base = len(CORPUS)
    for i, chunk in enumerate(chunks):
        CORPUS.append(
            Document(
                doc_id=f"ingest-{base + i}",
                text=chunk,
                metadata=metadata or {"doc_category": "INGESTED"},
                source="api_ingest",
            )
        )
    _cache.invalidate()
    return len(chunks)
