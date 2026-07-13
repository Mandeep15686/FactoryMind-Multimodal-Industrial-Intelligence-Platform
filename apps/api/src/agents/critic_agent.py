"""Critic Agent — validates RCA grounding/consistency, gates refinement loop."""
from __future__ import annotations

from src.agents.state import FactoryMindState
from src.core.config import settings
from src.core.observability import trace_span


def critic_agent_node(state: FactoryMindState) -> dict:
    with trace_span("critic_agent", iter=state.get("rca_iterations", 0)):
        hypothesis = state.get("rca_hypothesis") or ""
        evidence = state.get("evidence", []) or []
        docs = state.get("retrieved_docs", []) or []

        grounded = _is_grounded(hypothesis, state.get("root_causes", []), docs)
        consistent = bool(hypothesis) and len(evidence) >= 2
        base_conf = float(state.get("confidence", 0.0))

        # Adjust confidence for grounding + consistency.
        confidence = base_conf
        if not grounded:
            confidence *= 0.7
        if not consistent:
            confidence *= 0.8
        confidence = round(min(confidence, 0.99), 3)

        feedback = None
        if confidence < settings.critic_confidence_threshold:
            issues = []
            if not grounded:
                issues.append("root causes are not clearly traceable to retrieved documents")
            if not consistent:
                issues.append("insufficient corroborating evidence (need >= 2 grounded facts)")
            feedback = (
                "Refine the diagnosis: " + "; ".join(issues or ["increase evidence specificity"]) + "."
            )

        return {
            "confidence": confidence,
            "critic_feedback": feedback,
            "rca_iterations": state.get("rca_iterations", 0) + 1,
        }


def _is_grounded(hypothesis: str, root_causes: list[str], docs: list) -> bool:
    if not docs:
        return False
    corpus = " ".join(getattr(d, "text", "").lower() for d in docs)
    terms = (hypothesis + " " + " ".join(root_causes)).lower().split()
    key_terms = [t for t in terms if len(t) > 5]
    if not key_terms:
        return False
    hits = sum(1 for t in key_terms if t in corpus)
    return hits / len(key_terms) >= 0.15


def route_from_critic(state: FactoryMindState) -> str:
    """Loop back to RCA if under-confident and iterations remain."""
    confident = float(state.get("confidence", 0.0)) >= settings.critic_confidence_threshold
    exhausted = state.get("rca_iterations", 0) >= settings.max_rca_iterations
    if confident or exhausted:
        return "maintenance_planning"
    return "rca_agent"
