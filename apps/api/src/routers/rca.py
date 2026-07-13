"""RCA endpoints."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from src.agents.graph import run_graph
from src.core.exceptions import NotFoundError
from src.core.security import CurrentPrincipal
from src.models.schemas import IoTEvent, EventType, RCAFeedback

router = APIRouter(tags=["rca"])

_RCA: dict[str, dict] = {
    "rca-1": {"id": "rca-1", "machine_id": "M12", "hypothesis": "Drive-end bearing wear", "confidence": 0.83, "retrieved_docs": ["kb-001", "kb-006"]},
    "rca-2": {"id": "rca-2", "machine_id": "P07", "hypothesis": "Belt misalignment", "confidence": 0.79, "retrieved_docs": ["kb-003"]},
}


class RCATrigger(BaseModel):
    machine_id: str


def get_rca_record(rca_id: str) -> dict:
    rec = _RCA.get(rca_id)
    if not rec:
        raise NotFoundError(f"RCA {rca_id} not found")
    return rec


@router.post("/rca")
async def trigger_rca(req: RCATrigger, principal: CurrentPrincipal) -> dict:
    event = IoTEvent(
        event_id=f"evt-{uuid.uuid4().hex[:12]}",
        plant_id=principal.plant_id or "plant-demo",
        machine_id=req.machine_id,
        shift_id="shift-demo",
        event_type=EventType.SENSOR_THRESHOLD,
    )
    final = run_graph(event)
    rca_id = f"rca-{uuid.uuid4().hex[:8]}"
    record = {
        "id": rca_id,
        "machine_id": req.machine_id,
        "hypothesis": final.get("rca_hypothesis"),
        "root_causes": final.get("root_causes", []),
        "recommendations": final.get("recommendations", []),
        "confidence": final.get("confidence"),
        "evidence": final.get("evidence", []),
        "retrieved_docs": [getattr(d, "doc_id", str(d)) for d in final.get("retrieved_docs", [])],
        "created_at": datetime.utcnow().isoformat(),
    }
    _RCA[rca_id] = record
    return record


@router.get("/rca/{rca_id}")
async def get_rca(rca_id: str, principal: CurrentPrincipal) -> dict:
    return get_rca_record(rca_id)


@router.post("/rca/{rca_id}/feedback")
async def submit_feedback(rca_id: str, feedback: RCAFeedback, principal: CurrentPrincipal) -> dict:
    rec = get_rca_record(rca_id)
    rec["engineer_verdict"] = feedback.verdict
    rec["feedback_notes"] = feedback.notes
    rec["feedback_by"] = principal.sub
    return {"status": "recorded", "rca_id": rca_id, "verdict": feedback.verdict}


@router.get("/rca/{rca_id}/evidence")
async def get_evidence(rca_id: str, principal: CurrentPrincipal) -> dict:
    rec = get_rca_record(rca_id)
    return {"rca_id": rca_id, "retrieved_docs": rec.get("retrieved_docs", []), "evidence": rec.get("evidence", [])}
