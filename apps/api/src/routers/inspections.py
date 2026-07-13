"""Inspection & defect endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter

from src.agents.graph import run_graph
from src.core.security import CurrentPrincipal
from src.hf_tasks.visual_qa import ask as vqa_ask
from src.models.schemas import (
    ImageFrame,
    InspectionRequest,
    IoTEvent,
    EventType,
    VQARequest,
)

router = APIRouter(tags=["inspections"])

# in-memory store for the scaffold
_INSPECTIONS: dict[str, dict] = {}


@router.post("/inspections")
async def trigger_inspection(req: InspectionRequest, principal: CurrentPrincipal) -> dict:
    """Trigger a manual inspection and run the full agent graph."""
    event_id = f"evt-{uuid.uuid4().hex[:12]}"
    frames = [
        ImageFrame(
            frame_id=f"f-{i}", machine_id=req.machine_id, s3_url=url, captured_at=datetime.utcnow()
        )
        for i, url in enumerate(req.image_urls or [f"s3://mock/{req.machine_id}/frame0.jpg"])
    ]
    event = IoTEvent(
        event_id=event_id,
        plant_id=principal.plant_id or "plant-demo",
        machine_id=req.machine_id,
        shift_id="shift-demo",
        event_type=EventType.SCHEDULED_INSPECTION,
        frames=frames,
    )
    final = run_graph(event)
    defects = final.get("defects", [])
    record = {
        "id": event_id,
        "machine_id": req.machine_id,
        "triggered_by": req.triggered_by,
        "defects": [d.model_dump() if hasattr(d, "model_dump") else d for d in defects],
        "defect_severity": final.get("defect_severity"),
        "jira_ticket_id": final.get("jira_ticket_id"),
        "rca_hypothesis": final.get("rca_hypothesis"),
        "created_at": datetime.utcnow().isoformat(),
    }
    _INSPECTIONS[event_id] = record
    return record


@router.get("/inspections/{inspection_id}")
async def get_inspection(inspection_id: str, principal: CurrentPrincipal) -> dict:
    from src.core.exceptions import NotFoundError

    rec = _INSPECTIONS.get(inspection_id)
    if not rec:
        raise NotFoundError(f"Inspection {inspection_id} not found")
    return rec


@router.get("/machines/{machine_id}/inspections")
async def list_machine_inspections(machine_id: str, principal: CurrentPrincipal) -> list[dict]:
    return [r for r in _INSPECTIONS.values() if r["machine_id"] == machine_id]


@router.post("/defects/{defect_id}/query")
async def query_defect(defect_id: str, req: VQARequest, principal: CurrentPrincipal) -> dict:
    """Visual Question Answering over a defect image."""
    image_url = f"s3://mock/defects/{defect_id}.jpg"
    answer = vqa_ask(image_url, req.question)
    return {"defect_id": defect_id, "question": req.question, "answer": answer}
