"""LangGraph assembly for the FactoryMind multi-agent pipeline.

Topology (blueprint Section 7 / 12):
    START → supervisor → {visual, audio, sensor} (parallel Send)
          → knowledge_retrieval → rca_agent ⇄ critic_agent (retry loop, max 3)
          → maintenance_planning → [human_approval?] → alert_agent
          → report_generation → feedback → END

If ``langgraph`` is unavailable, a minimal sequential ``_FallbackGraph`` runs the
same node functions so the pipeline works in constrained environments.
"""
from __future__ import annotations

from typing import Any

from src.agents.alert_agent import alert_agent_node
from src.agents.audio_analysis import audio_analysis_node
from src.agents.critic_agent import critic_agent_node, route_from_critic
from src.agents.feedback_agent import feedback_node
from src.agents.human_approval import human_approval_node
from src.agents.knowledge_retrieval import knowledge_retrieval_node
from src.agents.maintenance_planning import maintenance_planning_node, route_from_planning
from src.agents.rca_agent import rca_agent_node
from src.agents.report_generation import report_generation_node
from src.agents.sensor_analysis import sensor_analysis_node
from src.agents.state import FactoryMindState
from src.agents.supervisor import route_from_supervisor, supervisor_node
from src.agents.visual_inspection import visual_inspection_node

_NODES = {
    "supervisor": supervisor_node,
    "visual_inspection": visual_inspection_node,
    "audio_analysis": audio_analysis_node,
    "sensor_analysis": sensor_analysis_node,
    "knowledge_retrieval": knowledge_retrieval_node,
    "rca_agent": rca_agent_node,
    "critic_agent": critic_agent_node,
    "maintenance_planning": maintenance_planning_node,
    "human_approval": human_approval_node,
    "alert_agent": alert_agent_node,
    "report_generation": report_generation_node,
    "feedback": feedback_node,
}


# ══════════════════════════════════════════════════════════
#  LangGraph builder
# ══════════════════════════════════════════════════════════
def build_graph():
    """Compile and return the LangGraph, or a sequential fallback."""
    try:
        from langgraph.graph import END, START, StateGraph

        g = StateGraph(FactoryMindState)
        for name, fn in _NODES.items():
            g.add_node(name, fn)

        g.add_edge(START, "supervisor")
        # parallel fan-out via conditional edges (Send)
        g.add_conditional_edges(
            "supervisor",
            route_from_supervisor,
            ["visual_inspection", "audio_analysis", "sensor_analysis"],
        )
        # specialists converge on knowledge retrieval
        for specialist in ("visual_inspection", "audio_analysis", "sensor_analysis"):
            g.add_edge(specialist, "knowledge_retrieval")
        g.add_edge("knowledge_retrieval", "rca_agent")
        g.add_edge("rca_agent", "critic_agent")
        g.add_conditional_edges(
            "critic_agent", route_from_critic, ["rca_agent", "maintenance_planning"]
        )
        g.add_conditional_edges(
            "maintenance_planning", route_from_planning, ["human_approval", "alert_agent"]
        )
        g.add_edge("human_approval", "alert_agent")
        g.add_edge("alert_agent", "report_generation")
        g.add_edge("report_generation", "feedback")
        g.add_edge("feedback", END)

        try:
            from langgraph.checkpoint.memory import MemorySaver

            return g.compile(checkpointer=MemorySaver())
        except Exception:
            return g.compile()
    except Exception:
        return _FallbackGraph()


# ══════════════════════════════════════════════════════════
#  Sequential fallback executor
# ══════════════════════════════════════════════════════════
class _FallbackGraph:
    """Runs the nodes in dependency order without langgraph installed."""

    def invoke(self, state: FactoryMindState, config: dict | None = None) -> FactoryMindState:
        state = dict(state)  # type: ignore[assignment]
        _merge(state, supervisor_node(state))

        for specialist in state.get("active_agents", []):
            fn = _NODES.get(specialist)
            if fn:
                _merge(state, fn(state))

        _merge(state, knowledge_retrieval_node(state))

        # RCA ⇄ Critic loop
        while True:
            _merge(state, rca_agent_node(state))
            _merge(state, critic_agent_node(state))
            if route_from_critic(state) == "maintenance_planning":
                break

        _merge(state, maintenance_planning_node(state))
        if route_from_planning(state) == "human_approval":
            _merge(state, human_approval_node(state))
        _merge(state, alert_agent_node(state))
        _merge(state, report_generation_node(state))
        _merge(state, feedback_node(state))
        return state  # type: ignore[return-value]


def _merge(state: dict, update: dict[str, Any] | None) -> None:
    if update:
        state.update(update)


# ══════════════════════════════════════════════════════════
#  Convenience runner
# ══════════════════════════════════════════════════════════
def run_graph(event: Any) -> FactoryMindState:
    """Convert an IoTEvent (or dict) to initial state and run the graph."""
    initial = _event_to_state(event)
    graph = build_graph()
    config = {"configurable": {"thread_id": initial.get("event_id", "default")}}
    try:
        return graph.invoke(initial, config)  # type: ignore[arg-type]
    except TypeError:
        return graph.invoke(initial)  # fallback graph ignores config


def _event_to_state(event: Any) -> FactoryMindState:
    if hasattr(event, "model_dump"):
        data = event.model_dump()
    elif isinstance(event, dict):
        data = dict(event)
    else:
        data = {}
    # Preserve rich pydantic objects for frames/audio/sensor where present.
    if hasattr(event, "frames"):
        data["frames"] = event.frames
        data["audio_windows"] = event.audio_windows
        data["sensor_snapshot"] = event.sensor_snapshot
    state: FactoryMindState = {
        "event_id": data.get("event_id", "evt-unknown"),
        "plant_id": data.get("plant_id", ""),
        "machine_id": data.get("machine_id", ""),
        "shift_id": data.get("shift_id", ""),
        "event_type": str(data.get("event_type", "")),
        "frames": data.get("frames", []),
        "audio_windows": data.get("audio_windows", []),
        "sensor_snapshot": data.get("sensor_snapshot"),
    }
    return state
