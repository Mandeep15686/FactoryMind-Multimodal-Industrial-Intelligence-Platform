"""Maintenance Planning Agent — build work order, check inventory, open Jira."""
from __future__ import annotations

from src.agents.state import FactoryMindState
from src.core.config import settings
from src.core.observability import trace_span
from src.models.schemas import MaintenancePlan, Priority, Severity
from src.tools.jira_tool import create_ticket
from src.tools.sap_tool import check_inventory

# severity → (urgency, priority, base hours)
_SEVERITY_MAP = {
    "CRITICAL": ("1h", Priority.P0, 4.0),
    "MAJOR": ("4h", Priority.P1, 2.5),
    "MINOR": ("24h", Priority.P2, 1.0),
    "NONE": ("7d", Priority.P3, 0.5),
}


def maintenance_planning_node(state: FactoryMindState) -> dict:
    with trace_span("maintenance_planning", machine_id=state.get("machine_id")):
        severity = state.get("defect_severity", "MINOR")
        # Escalate on imminent RUL regardless of visual severity.
        rul = state.get("rul_hours")
        if rul is not None and rul < 24 and severity in ("NONE", "MINOR"):
            severity = "MAJOR"

        urgency, priority, hours = _SEVERITY_MAP.get(severity, _SEVERITY_MAP["MINOR"])
        parts = _parts_from_recommendations(state)
        inventory = check_inventory(parts)
        parts_available = all(inventory.values()) if parts else True
        est_cost = _estimate_cost(parts)

        plan = MaintenancePlan(
            required_parts=parts,
            estimated_hours=hours,
            technician_skill="SENIOR" if priority in (Priority.P0, Priority.P1) else "STANDARD",
            urgency=urgency,
            priority=priority,
            estimated_cost_usd=est_cost,
            parts_available=parts_available,
        )

        summary = f"[{priority.value}] {severity} issue on {state.get('machine_id')}"
        description = _ticket_body(state, plan)
        ticket_id = create_ticket(
            summary=summary,
            description=description,
            priority=priority.value,
            machine_id=state.get("machine_id", ""),
            parts=parts,
        )

        needs_approval = priority == Priority.P0 or est_cost > settings.high_cost_approval_usd
        return {
            "maintenance_plan": plan,
            "jira_ticket_id": ticket_id,
            "needs_human_approval": needs_approval,
        }


def _parts_from_recommendations(state: FactoryMindState) -> list[str]:
    import re

    text = " ".join(state.get("recommendations", []) or [])
    codes = re.findall(r"[A-Z]{2,}-\d+(?:-[A-Z0-9]+)*", text)
    return list(dict.fromkeys(codes)) or (["SKF-22222-E-C3"] if state.get("root_causes") else [])


def _estimate_cost(parts: list[str]) -> float:
    return round(sum(1200.0 for _ in parts), 2)


def _ticket_body(state: FactoryMindState, plan: MaintenancePlan) -> str:
    lines = [
        f"Root cause hypothesis: {state.get('rca_hypothesis', 'N/A')}",
        f"Confidence: {state.get('confidence')}",
        "Recommendations:",
        *[f"  - {r}" for r in state.get("recommendations", []) or []],
        f"Required parts: {', '.join(plan.required_parts) or 'none'}",
        f"Estimated downtime: {plan.estimated_hours}h | Urgency: {plan.urgency}",
    ]
    return "\n".join(lines)


def route_from_planning(state: FactoryMindState) -> str:
    return "human_approval" if state.get("needs_human_approval") else "alert_agent"
