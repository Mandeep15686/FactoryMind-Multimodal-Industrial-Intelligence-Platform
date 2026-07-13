"""Alert Agent — routes notifications by severity × urgency matrix."""
from __future__ import annotations

from src.agents.state import FactoryMindState
from src.core.observability import trace_span
from src.tools.pagerduty_tool import trigger_incident
from src.tools.slack_tool import notify


def alert_agent_node(state: FactoryMindState) -> dict:
    with trace_span("alert_agent", machine_id=state.get("machine_id")):
        plan = state.get("maintenance_plan")
        priority = getattr(getattr(plan, "priority", None), "value", "P2")
        machine_id = state.get("machine_id", "unknown")
        ticket = state.get("jira_ticket_id", "N/A")
        summary = f"{priority} — {state.get('defect_severity', 'MINOR')} on {machine_id} (ticket {ticket})"

        if priority == "P0":
            trigger_incident(summary=summary, severity="critical", machine_id=machine_id)
            notify("#plant-critical", f"<!here> {summary}", severity="CRITICAL")
        elif priority == "P1":
            notify("#plant-maintenance", summary, severity="MAJOR")
        else:
            notify("#plant-maintenance", summary, severity="INFO")

        return {"alert_sent": True}
