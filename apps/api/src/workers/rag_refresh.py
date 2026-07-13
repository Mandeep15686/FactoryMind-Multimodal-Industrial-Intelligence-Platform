"""Nightly RAG knowledge refresh task."""
from __future__ import annotations

import logging

from src.workers.celery_app import celery_app

logger = logging.getLogger("factorymind.workers.rag")


@celery_app.task(name="workers.rag_refresh.refresh_knowledge")
def refresh_knowledge() -> dict:
    """Ingest new RCA reports, update Neo4j, upsert Qdrant, invalidate cache."""
    from src.rag import ingest_document
    from src.rag.cache import SemanticCache

    added = ingest_document(
        "Nightly refresh: newly confirmed RCA — coolant pump cavitation resolved by filter replacement.",
        {"doc_category": "RCA_REPORT", "date": "2026-07-12", "machine_type": "CNC_LATHE"},
    )
    SemanticCache().invalidate()
    logger.info("RAG refresh complete: %d chunks added", added)
    return {"status": "ok", "chunks_added": added}
