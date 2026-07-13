"""WebSocket endpoints — real-time alert / inspection / agent-trace streams."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.hf_tasks._client import seeded_rng

router = APIRouter(tags=["websocket"])


async def _stream(ws: WebSocket, make_frame, interval: float = 2.0, limit: int = 20) -> None:
    await ws.accept()
    try:
        for i in range(limit):
            await ws.send_text(json.dumps(make_frame(i)))
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        return
    except Exception:
        return


@router.websocket("/ws/alerts/{plant_id}")
async def ws_alerts(ws: WebSocket, plant_id: str) -> None:
    rng = seeded_rng("wsalert:" + plant_id)

    def frame(i: int) -> dict:
        return {
            "type": "alert",
            "plant_id": plant_id,
            "seq": i,
            "machine_id": rng.choice(["M05", "M12", "P07"]),
            "severity": rng.choice(["MINOR", "MAJOR", "CRITICAL"]),
            "ts": datetime.utcnow().isoformat(),
        }

    await _stream(ws, frame)


@router.websocket("/ws/inspection/{machine_id}")
async def ws_inspection(ws: WebSocket, machine_id: str) -> None:
    rng = seeded_rng("wsinsp:" + machine_id)

    def frame(i: int) -> dict:
        return {
            "type": "defect",
            "machine_id": machine_id,
            "frame": i,
            "detections": rng.randint(0, 3),
            "fps": 30,
            "ts": datetime.utcnow().isoformat(),
        }

    await _stream(ws, frame, interval=1.0)


@router.websocket("/ws/agent-trace/{event_id}")
async def ws_agent_trace(ws: WebSocket, event_id: str) -> None:
    steps = [
        "supervisor", "visual_inspection", "audio_analysis", "sensor_analysis",
        "knowledge_retrieval", "rca_agent", "critic_agent", "maintenance_planning",
        "alert_agent", "report_generation", "feedback",
    ]

    def frame(i: int) -> dict:
        return {
            "type": "agent_step",
            "event_id": event_id,
            "step": steps[i] if i < len(steps) else "done",
            "index": i,
            "ts": datetime.utcnow().isoformat(),
        }

    await _stream(ws, frame, interval=0.8, limit=len(steps))
