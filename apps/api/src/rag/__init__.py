"""FactoryMind RAG package — hybrid Graph RAG with Self-RAG quality gating."""

from src.rag.pipeline import ingest_document, retrieve_knowledge  # noqa: F401

__all__ = ["retrieve_knowledge", "ingest_document"]
