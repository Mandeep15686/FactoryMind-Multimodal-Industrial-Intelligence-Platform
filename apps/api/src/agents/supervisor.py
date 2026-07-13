"""Supervisor Agent — classifies events and fans out to specialist agents."""
from __future__ import annotations

from src.agents.state import FactoryMindState
from src.core.observability import trace_span


def supervisor_node(state: FactoryMindState) -> dict:
    """Classify the event and initialize control fields."""
    with trace_span("supervisor", event_id=state.get("event_id")):
        active: list[str] = []
        if state.get("frames"):
            active.append("visual_inspection")
        if state.get("audio_windows"):
            active.append("audio_analysis")
        if state.get("sensor_snapshot"):
            active.append("sensor_analysis")
        if not active:
            # scheduled inspection with no signals — still run vision by default
            active.append("visual_inspection")
        return {
            "active_agents": active,
            "rca_iterations": 0,
            "alert_sent": False,
            "needs_human_approval": False,
            "errors": [],
        }


def route_from_supervisor(state: FactoryMindState):
    """Fan out to the active specialist agents in parallel via ``Send``."""
    try:
        from langgraph.constants import Send

        return [Send(agent, state) for agent in state.get("active_agents", ["visual_inspection"])]
    except Exception:
        # Fallback executor handles routing itself.
        return state.get("active_agents", ["visual_inspection"])
