"""Maintenance ticket + RUL endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.core.exceptions import NotFoundError
from src.core.security import CurrentPrincipal
from src.hf_tasks import time_series_forecast
from src.tools.jira_tool import create_ticket, update_ticket

router = APIRouter(tags=["maintenance"])

_TICKETS: dict[str, dict] = {}


class TicketCreate(BaseModel):
    machine_id: str
    summary: str
    description: str = ""
    priority: str = "P2"
    parts: list[str] = []


class TicketUpdate(BaseModel):
    status: str | None = None
    assigned_to: str | None = None


@router.get("/maintenance")
async def list_tickets(
    principal: CurrentPrincipal,
    status: str | None = Query(None),
    priority: str | None = Query(None),
) -> list[dict]:
    tickets = list(_TICKETS.values())
    if status:
        tickets = [t for t in tickets if t["status"] == status]
    if priority:
        tickets = [t for t in tickets if t["priority"] == priority]
    return tickets


@router.post("/maintenance")
async def create_maintenance(req: TicketCreate, principal: CurrentPrincipal) -> dict:
    jira_id = create_ticket(req.summary, req.description, req.priority, req.machine_id, req.parts)
    ticket = {
        "id": f"tkt-{uuid.uuid4().hex[:8]}",
        "jira_ticket_id": jira_id,
        "machine_id": req.machine_id,
        "priority": req.priority,
        "status": "OPEN",
        "required_parts": req.parts,
    }
    _TICKETS[ticket["id"]] = ticket
    return ticket


@router.patch("/maintenance/{ticket_id}")
async def patch_maintenance(ticket_id: str, req: TicketUpdate, principal: CurrentPrincipal) -> dict:
    ticket = _TICKETS.get(ticket_id)
    if not ticket:
        raise NotFoundError(f"Ticket {ticket_id} not found")
    if req.status:
        ticket["status"] = req.status
        update_ticket(ticket["jira_ticket_id"], req.status)
    if req.assigned_to:
        ticket["assigned_to"] = req.assigned_to
    return ticket


@router.get("/machines/{machine_id}/rul")
async def get_rul(machine_id: str, principal: CurrentPrincipal) -> dict:
    forecast = time_series_forecast.forecast([45.0 + i * 0.3 for i in range(168)], machine_id=machine_id)
    return {
        "machine_id": machine_id,
        "rul_hours": forecast.rul_hours,
        "health_state": forecast.health_state.value,
        "trend": forecast.trend,
        "horizon_hours": forecast.horizon_hours,
    }
