"""RAG pipeline unit tests."""
from __future__ import annotations

from src.rag import retrieve_knowledge
from src.rag.retrieval.hybrid import reciprocal_rank_fusion
from src.models.schemas import Document


def test_retrieve_returns_documents():
    result = retrieve_knowledge("bearing wear vibration drive end", machine_type="CONVEYOR")
    assert len(result.documents) > 0
    assert 0.0 <= result.retrieval_score <= 1.0
    assert result.query_variants


def test_rrf_orders_by_fused_score():
    a = Document(doc_id="1", text="x")
    b = Document(doc_id="2", text="y")
    fused = reciprocal_rank_fusion([[a, b], [b, a]])
    ids = {d.doc_id for d in fused}
    assert ids == {"1", "2"}


def test_graph_paths_present_for_known_type():
    result = retrieve_knowledge("belt misalignment sheave", machine_type="PRESS")
    assert isinstance(result.graph_paths, list)
