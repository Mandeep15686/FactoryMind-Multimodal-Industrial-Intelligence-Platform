"""Knowledge base endpoints — semantic search + ingestion."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from src.core.security import CurrentPrincipal, Role, require_role
from src.models.schemas import KnowledgeQuery
from src.rag import ingest_document, retrieve_knowledge

router = APIRouter(tags=["knowledge"])


class IngestRequest(BaseModel):
    text: str
    metadata: dict = {}


@router.post("/knowledge/query")
async def query_knowledge(req: KnowledgeQuery, principal: CurrentPrincipal) -> dict:
    result = retrieve_knowledge(req.query, machine_type=req.machine_type, plant_id=req.plant_id)
    return {
        "query": req.query,
        "retrieval_score": result.retrieval_score,
        "query_variants": result.query_variants,
        "graph_paths": result.graph_paths,
        "documents": [d.model_dump() for d in result.documents[: req.top_k]],
    }


@router.post("/knowledge/ingest")
async def ingest(req: IngestRequest, principal: CurrentPrincipal) -> dict:
    n = ingest_document(req.text, req.metadata)
    return {"status": "ingested", "chunks_added": n}


@router.delete("/knowledge/docs/{doc_id}")
async def delete_doc(doc_id: str, _=require_role(Role.ADMIN, Role.QUALITY_ENGINEER)) -> dict:
    from src.rag._corpus import CORPUS

    before = len(CORPUS)
    CORPUS[:] = [d for d in CORPUS if d.doc_id != doc_id]
    return {"status": "deleted", "removed": before - len(CORPUS), "doc_id": doc_id}
