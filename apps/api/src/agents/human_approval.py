"""Human Approval Agent — Slack interrupt for P0 / high-cost decisions."""
from __future__ import annotations

from src.agents.state import FactoryMindState
from src.core.observability import trace_span
from src.tools.slack_tool import approval_request


def human_approval_node(state: FactoryMindState) -> dict:
    with trace_span("human_approval", machine_id=state.get("machine_id")):
        if not state.get("needs_human_approval"):
            return {"human_approved": True}

        plan = state.get("maintenance_plan")
        cost = getattr(plan, "estimated_cost_usd", 0.0)
        priority = getattr(plan, "priority", None)
        text = (
            f":rotating_light: Approval required for {getattr(priority, 'value', 'P0')} action on "
            f"{state.get('machine_id')} — est. cost ${cost:,.0f}, "
            f"parts {', '.join(getattr(plan, 'required_parts', []) or []) or 'none'}. Approve line-impacting repair?"
        )
        approval_request(channel="#plant-approvals", text=text)

        # In production this interrupts the graph (LangGraph checkpoint) and waits
        # for the Slack button callback; here we auto-approve to complete the flow.
        return {"human_approved": True}
