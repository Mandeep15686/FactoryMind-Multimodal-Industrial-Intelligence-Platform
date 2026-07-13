"""LangGraph typed state machine for FactoryMind.

``FactoryMindState`` is the single shared state object threaded through every
agent node. Nodes read the signals they need and write their structured
results back. This mirrors the blueprint spec exactly.
"""
from __future__ import annotations

from typing import Optional, TypedDict

from src.models.schemas import (
    AudioAnomaly,
    Defect,
    Document,
    ImageFrame,
    AudioWindow,
    MaintenancePlan,
    SensorSnapshot,
)


class FactoryMindState(TypedDict, total=False):
    # ── Input signals ──────────────────────────────
    event_id: str
    plant_id: str
    machine_id: str
    shift_id: str
    event_type: str
    frames: list[ImageFrame]
    audio_windows: list[AudioWindow]
    sensor_snapshot: Optional[SensorSnapshot]

    # ── Vision results ─────────────────────────────
    defects: list[Defect]
    defect_severity: str  # CRITICAL/MAJOR/MINOR/NONE

    # ── Audio results ──────────────────────────────
    audio_anomaly: Optional[AudioAnomaly]

    # ── Sensor forecast ────────────────────────────
    rul_hours: Optional[float]
    health_state: str  # HEALTHY/DEGRADED/CRITICAL

    # ── RAG retrieval ──────────────────────────────
    retrieved_docs: list[Document]
    retrieval_score: float
    query_variants: list[str]

    # ── RCA reasoning ──────────────────────────────
    rca_hypothesis: Optional[str]
    root_causes: list[str]
    confidence: float
    evidence: list[str]
    critic_feedback: Optional[str]
    rca_iterations: int  # max 3 critique loops

    # ── Outputs ────────────────────────────────────
    maintenance_plan: Optional[MaintenancePlan]
    jira_ticket_id: Optional[str]
    alert_sent: bool
    shift_report: Optional[str]
    human_approved: Optional[bool]

    # ── Routing / control ──────────────────────────
    active_agents: list[str]
    needs_human_approval: bool
    errors: list[str]
