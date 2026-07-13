"""Report Generation Agent — shift summary via HF summarization + LLM polish."""
from __future__ import annotations

from src.agents.llm import call_llm
from src.agents.state import FactoryMindState
from src.core.observability import trace_span
from src.hf_tasks import summarization

_SYSTEM = (
    "You are writing an executive shift handover report for a plant manager. Be concise, "
    "structured, and action-oriented. Use Markdown with sections: Summary, Key Events, "
    "Maintenance Actions, Recommendations."
)


def report_generation_node(state: FactoryMindState) -> dict:
    with trace_span("report_generation", machine_id=state.get("machine_id")):
        events = _collect_events(state)
        draft = summarization.summarize(events, max_words=250)
        report = call_llm(_SYSTEM, f"Shift event digest:\n{draft}\n\nWrite the report.")
        return {"shift_report": report}


def _collect_events(state: FactoryMindState) -> str:
    lines = [f"Machine {state.get('machine_id')} in plant {state.get('plant_id')}."]
    for d in state.get("defects", []) or []:
        dt = getattr(getattr(d, "defect_type", None), "value", "")
        sev = getattr(getattr(d, "severity", None), "value", "")
        lines.append(f"Detected {sev} {dt} defect with confidence {getattr(d, 'confidence', 0)}.")
    audio = state.get("audio_anomaly")
    if audio is not None:
        lines.append(f"Acoustic anomaly {getattr(audio, 'anomaly_class', '')} observed.")
    if state.get("health_state"):
        lines.append(f"Sensor health {state['health_state']}, remaining useful life {state.get('rul_hours')} hours.")
    if state.get("rca_hypothesis"):
        lines.append(f"Root cause analysis concluded: {state['rca_hypothesis']}.")
    if state.get("jira_ticket_id"):
        lines.append(f"Maintenance ticket {state['jira_ticket_id']} was created.")
    for r in state.get("recommendations", []) or []:
        lines.append(f"Recommended action: {r}.")
    return " ".join(lines)
