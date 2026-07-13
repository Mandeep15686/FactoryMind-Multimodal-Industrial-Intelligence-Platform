"""Pydantic schemas — the shared data contracts across all agents, HF task
wrappers, RAG components, tools, and API routers.

These are the canonical structured types referenced by the LangGraph
``FactoryMindState`` and by every service boundary.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════
#  Enums
# ══════════════════════════════════════════════════════════
class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    NONE = "NONE"


class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"


class DefectType(str, Enum):
    CRACK = "CRACK"
    SCRATCH = "SCRATCH"
    CONTAMINATION = "CONTAMINATION"
    MISALIGNMENT = "MISALIGNMENT"
    UNKNOWN = "UNKNOWN"


class EventType(str, Enum):
    VISUAL_ANOMALY = "VISUAL_ANOMALY"
    AUDIO_ANOMALY = "AUDIO_ANOMALY"
    SENSOR_THRESHOLD = "SENSOR_THRESHOLD"
    SCHEDULED_INSPECTION = "SCHEDULED_INSPECTION"


class Priority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


# ══════════════════════════════════════════════════════════
#  Input signals
# ══════════════════════════════════════════════════════════
class ImageFrame(BaseModel):
    frame_id: str
    machine_id: str
    s3_url: str
    captured_at: datetime
    width: int = 1920
    height: int = 1080


class AudioWindow(BaseModel):
    window_id: str
    machine_id: str
    s3_url: str
    sample_rate: int = 16_000
    duration_s: float = 1.0
    captured_at: datetime


class SensorReading(BaseModel):
    sensor_type: str  # VIBRATION / TEMPERATURE / PRESSURE
    value: float
    unit: str
    anomaly_score: float = 0.0
    ts: datetime


class SensorSnapshot(BaseModel):
    machine_id: str
    readings: list[SensorReading] = Field(default_factory=list)
    window_start: Optional[datetime] = None
    window_end: Optional[datetime] = None


# ══════════════════════════════════════════════════════════
#  Vision / audio / sensor results
# ══════════════════════════════════════════════════════════
class BoundingBox(BaseModel):
    x: float
    y: float
    w: float
    h: float
    image_url: Optional[str] = None


class Defect(BaseModel):
    defect_type: DefectType = DefectType.UNKNOWN
    severity: Severity = Severity.MINOR
    confidence: float = 0.0
    bbox: Optional[BoundingBox] = None
    area_mm2: Optional[float] = None
    description: Optional[str] = None
    visual_embedding: Optional[list[float]] = None
    similar_defect_ids: list[str] = Field(default_factory=list)


class AudioAnomaly(BaseModel):
    anomaly_class: str
    score: float
    baseline_deviation: float
    transcript: Optional[str] = None
    entities: list["Entity"] = Field(default_factory=list)


class Entity(BaseModel):
    label: str  # MACHINE_ID / PART_NUMBER / ERROR_CODE / FAILURE_MODE / CORRECTIVE_ACTION
    text: str
    start: int = 0
    end: int = 0
    score: float = 1.0


class SensorForecast(BaseModel):
    machine_id: str
    horizon_hours: int = 72
    forecast: list[float] = Field(default_factory=list)
    rul_hours: Optional[float] = None
    health_state: HealthState = HealthState.HEALTHY
    trend: str = "STABLE"  # RISING / FALLING / STABLE


# ══════════════════════════════════════════════════════════
#  RAG
# ══════════════════════════════════════════════════════════
class Document(BaseModel):
    doc_id: str
    text: str
    score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)
    source: Optional[str] = None


class RetrievalResult(BaseModel):
    documents: list[Document] = Field(default_factory=list)
    retrieval_score: float = 0.0
    query_variants: list[str] = Field(default_factory=list)
    graph_paths: list[str] = Field(default_factory=list)


# ══════════════════════════════════════════════════════════
#  RCA + maintenance
# ══════════════════════════════════════════════════════════
class RootCause(BaseModel):
    cause: str
    probability: float
    evidence: list[str] = Field(default_factory=list)


class RCAResult(BaseModel):
    hypothesis: str
    root_causes: list[RootCause] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    evidence: list[str] = Field(default_factory=list)
    llm_model: Optional[str] = None
    prompt_version: Optional[str] = None


class CriticVerdict(BaseModel):
    confidence: float
    grounded: bool
    consistent: bool
    feedback: Optional[str] = None


class MaintenancePlan(BaseModel):
    required_parts: list[str] = Field(default_factory=list)
    estimated_hours: float = 1.0
    technician_skill: str = "STANDARD"
    urgency: str = "24h"  # 1h / 4h / 24h / 7d
    priority: Priority = Priority.P2
    estimated_cost_usd: float = 0.0
    parts_available: bool = True


# ══════════════════════════════════════════════════════════
#  Events / API payloads
# ══════════════════════════════════════════════════════════
class IoTEvent(BaseModel):
    event_id: str
    plant_id: str
    machine_id: str
    shift_id: str
    event_type: EventType
    frames: list[ImageFrame] = Field(default_factory=list)
    audio_windows: list[AudioWindow] = Field(default_factory=list)
    sensor_snapshot: Optional[SensorSnapshot] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InspectionRequest(BaseModel):
    machine_id: str
    triggered_by: str = "MANUAL"
    image_urls: list[str] = Field(default_factory=list)
    audio_urls: list[str] = Field(default_factory=list)


class VQARequest(BaseModel):
    question: str


class RCAFeedback(BaseModel):
    verdict: str  # CORRECT / PARTIAL / WRONG
    notes: Optional[str] = None


class KnowledgeQuery(BaseModel):
    query: str
    machine_type: Optional[str] = None
    plant_id: Optional[str] = None
    top_k: int = 5


AudioAnomaly.model_rebuild()
