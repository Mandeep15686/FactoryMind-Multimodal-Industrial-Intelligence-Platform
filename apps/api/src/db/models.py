"""SQLAlchemy ORM models mirroring the PostgreSQL/TimescaleDB schema
(blueprint Section 15). ``pgvector`` and TimescaleDB hypertable creation are
handled in Alembic migrations; here we keep the ORM portable.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class Plant(Base):
    __tablename__ = "plants"
    id: Mapped[uuid.UUID] = _uuid_pk()
    name: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(Text, default="UTC")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    machines: Mapped[list["Machine"]] = relationship(back_populates="plant")


class Machine(Base):
    __tablename__ = "machines"
    id: Mapped[uuid.UUID] = _uuid_pk()
    plant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plants.id"))
    name: Mapped[str] = mapped_column(Text, nullable=False)
    machine_type: Mapped[str | None] = mapped_column(Text)  # CNC_LATHE, PRESS, CONVEYOR
    manufacturer: Mapped[str | None] = mapped_column(Text)
    model_number: Mapped[str | None] = mapped_column(Text)
    install_date: Mapped[datetime | None] = mapped_column(DateTime)
    criticality: Mapped[str] = mapped_column(Text, default="MEDIUM")
    opc_ua_node_id: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    plant: Mapped[Plant] = relationship(back_populates="machines")


class Shift(Base):
    __tablename__ = "shifts"
    id: Mapped[uuid.UUID] = _uuid_pk()
    plant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plants.id"))
    name: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = _uuid_pk()
    email: Mapped[str] = mapped_column(String(320), unique=True)
    name: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text, default="technician")
    plant_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("plants.id"))


class SensorReading(Base):
    """TimescaleDB hypertable (see migration for create_hypertable)."""
    __tablename__ = "sensor_readings"
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    machine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("machines.id"), primary_key=True)
    sensor_type: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[float] = mapped_column(Float)
    anomaly_score: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str | None] = mapped_column(Text)


class Inspection(Base):
    __tablename__ = "inspections"
    id: Mapped[uuid.UUID] = _uuid_pk()
    machine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("machines.id"))
    shift_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("shifts.id"))
    triggered_by: Mapped[str | None] = mapped_column(Text)  # SCHEDULED/ALERT/MANUAL
    image_urls: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    audio_urls: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    defects: Mapped[list["Defect"]] = relationship(back_populates="inspection")


class Defect(Base):
    __tablename__ = "defects"
    id: Mapped[uuid.UUID] = _uuid_pk()
    inspection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inspections.id"))
    defect_type: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    bbox: Mapped[dict | None] = mapped_column(JSON)
    area_mm2: Mapped[float | None] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(Text)
    # visual_embedding VECTOR(1024) — added via pgvector in migration
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    inspection: Mapped[Inspection] = relationship(back_populates="defects")


class RCAReport(Base):
    __tablename__ = "rca_reports"
    id: Mapped[uuid.UUID] = _uuid_pk()
    machine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("machines.id"))
    alert_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    hypothesis: Mapped[str | None] = mapped_column(Text)
    root_causes: Mapped[dict | None] = mapped_column(JSON)
    recommendations: Mapped[dict | None] = mapped_column(JSON)
    confidence: Mapped[float | None] = mapped_column(Float)
    retrieved_docs: Mapped[dict | None] = mapped_column(JSON)
    llm_model: Mapped[str | None] = mapped_column(Text)
    prompt_version: Mapped[str | None] = mapped_column(Text)
    engineer_verdict: Mapped[str | None] = mapped_column(Text)  # CORRECT/PARTIAL/WRONG
    feedback_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MaintenanceTicket(Base):
    __tablename__ = "maintenance_tickets"
    id: Mapped[uuid.UUID] = _uuid_pk()
    machine_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("machines.id"))
    rca_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("rca_reports.id"))
    jira_ticket_id: Mapped[str | None] = mapped_column(Text, unique=True)
    priority: Mapped[str | None] = mapped_column(Text)  # P0/P1/P2/P3
    status: Mapped[str] = mapped_column(Text, default="OPEN")
    required_parts: Mapped[dict | None] = mapped_column(JSON)
    estimated_hrs: Mapped[float | None] = mapped_column(Float)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    id: Mapped[uuid.UUID] = _uuid_pk()
    name: Mapped[str | None] = mapped_column(Text)
    version: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    id: Mapped[uuid.UUID] = _uuid_pk()
    eval_type: Mapped[str | None] = mapped_column(Text)  # RAGAS/DEEPEVAL/CUSTOM
    prompt_version: Mapped[str | None] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(Text)
    dataset_version: Mapped[str | None] = mapped_column(Text)
    metrics: Mapped[dict | None] = mapped_column(JSON)
    pass_gate: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
