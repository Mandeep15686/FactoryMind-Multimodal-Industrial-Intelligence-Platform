"""RCA Agent — 5-Whys root cause reasoning over multimodal + RAG context."""
from __future__ import annotations

from src.agents.llm import call_llm_json
from src.agents.state import FactoryMindState
from src.core.config import settings
from src.core.observability import trace_span

_SYSTEM = (
    "You are a senior manufacturing reliability engineer. Using the 5-Whys methodology, "
    "diagnose the most probable root cause(s) from the multimodal evidence and the retrieved "
    "maintenance knowledge. Ground every claim in the provided evidence. Rank root causes by "
    "probability and provide concrete corrective recommendations."
)

_SCHEMA = {
    "hypothesis": "",
    "root_causes": [],
    "recommendations": [],
    "confidence": 0.0,
    "evidence": [],
}


def rca_agent_node(state: FactoryMindState) -> dict:
    with trace_span("rca_agent", machine_id=state.get("machine_id"), iter=state.get("rca_iterations", 0)):
        user = _build_context(state)
        if state.get("critic_feedback"):
            user += f"\n\nCRITIC FEEDBACK to address:\n{state['critic_feedback']}"

        result = call_llm_json(_SYSTEM, user, _SCHEMA)

        root_causes = result.get("root_causes", [])
        # normalize root_causes to list[str] for state while keeping details in evidence
        rc_strings = [
            rc["cause"] if isinstance(rc, dict) else str(rc) for rc in root_causes
        ]
        return {
            "rca_hypothesis": result.get("hypothesis", ""),
            "root_causes": rc_strings,
            "recommendations": result.get("recommendations", []),
            "confidence": float(result.get("confidence", 0.0)),
            "evidence": result.get("evidence", []),
            "_rca_detail": root_causes,  # retained for persistence layer
        }


def _build_context(state: FactoryMindState) -> str:
    lines = [f"Machine: {state.get('machine_id')} (plant {state.get('plant_id')})"]

    defects = state.get("defects", []) or []
    if defects:
        lines.append("Visual defects:")
        for d in defects:
            dt = getattr(getattr(d, "defect_type", None), "value", "")
            sev = getattr(getattr(d, "severity", None), "value", "")
            lines.append(f"  - {dt} severity={sev} conf={getattr(d, 'confidence', 0)} area={getattr(d, 'area_mm2', 0)}mm2")

    audio = state.get("audio_anomaly")
    if audio is not None:
        lines.append(
            f"Acoustic anomaly: {getattr(audio, 'anomaly_class', '')} "
            f"(score={getattr(audio, 'score', 0)}, deviation={getattr(audio, 'baseline_deviation', 0)})"
        )
        if getattr(audio, "transcript", None):
            lines.append(f"Technician note: {audio.transcript}")

    if state.get("health_state"):
        lines.append(f"Sensor health state: {state['health_state']}, RUL={state.get('rul_hours')}h")

    docs = state.get("retrieved_docs", []) or []
    if docs:
        lines.append("\nRetrieved knowledge:")
        for i, doc in enumerate(docs, 1):
            lines.append(f"  [{i}] {getattr(doc, 'text', '')}")

    return "\n".join(lines)


# expose the max-iteration constant for the graph builder
MAX_ITERATIONS = settings.max_rca_iterations
