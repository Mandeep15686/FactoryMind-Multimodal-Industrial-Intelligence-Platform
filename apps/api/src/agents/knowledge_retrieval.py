"""Knowledge Retrieval Agent — hybrid Graph RAG with Self-RAG re-query."""
from __future__ import annotations

from src.agents.state import FactoryMindState
from src.core.config import settings
from src.core.observability import trace_span
from src.rag import retrieve_knowledge


def knowledge_retrieval_node(state: FactoryMindState) -> dict:
    with trace_span("knowledge_retrieval", machine_id=state.get("machine_id")):
        query = _build_query(state)
        machine_type = _infer_machine_type(state)
        result = retrieve_knowledge(query, machine_type=machine_type, plant_id=state.get("plant_id"))

        # Self-RAG gate — pipeline already re-queries internally, but the agent
        # records the outcome and can expand once more if still weak.
        if result.retrieval_score < settings.self_rag_threshold:
            expanded = query + " root cause corrective action failure mode maintenance procedure"
            result = retrieve_knowledge(expanded, machine_type=machine_type)

        return {
            "retrieved_docs": result.documents,
            "retrieval_score": result.retrieval_score,
            "query_variants": result.query_variants,
        }


def _build_query(state: FactoryMindState) -> str:
    parts: list[str] = []
    for d in state.get("defects", []) or []:
        dt = getattr(d, "defect_type", None)
        parts.append(f"{getattr(dt, 'value', dt)} defect")
    audio = state.get("audio_anomaly")
    if audio is not None:
        parts.append(f"acoustic {getattr(audio, 'anomaly_class', '')}")
        for e in getattr(audio, "entities", []) or []:
            parts.append(getattr(e, "text", ""))
    if state.get("health_state") in ("DEGRADED", "CRITICAL"):
        parts.append(f"machine health {state['health_state'].lower()} rising trend")
    if state.get("rul_hours") is not None and state["rul_hours"] is not None:
        parts.append("remaining useful life imminent failure")
    return " ".join(p for p in parts if p) or "general machine health inspection"


def _infer_machine_type(state: FactoryMindState) -> str | None:
    # Would come from a machine lookup; None lets RAG search across types.
    return None
