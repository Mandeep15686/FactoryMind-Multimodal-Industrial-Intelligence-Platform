"""End-to-end smoke test — runs the full agent graph against mock HF outputs."""
from __future__ import annotations

from datetime import datetime

from src.agents.graph import build_graph, run_graph
from src.models.schemas import (
    AudioWindow,
    EventType,
    ImageFrame,
    IoTEvent,
    SensorReading,
    SensorSnapshot,
)


def _make_event() -> IoTEvent:
    now = datetime.utcnow()
    return IoTEvent(
        event_id="evt-smoke-1",
        plant_id="plant-demo",
        machine_id="M12",
        shift_id="shift-1",
        event_type=EventType.VISUAL_ANOMALY,
        frames=[ImageFrame(frame_id="f0", machine_id="M12", s3_url="s3://mock/m12/f0.jpg", captured_at=now)],
        audio_windows=[AudioWindow(window_id="w0", machine_id="M12", s3_url="s3://mock/m12/a0.wav", captured_at=now)],
        sensor_snapshot=SensorSnapshot(
            machine_id="M12",
            readings=[SensorReading(sensor_type="VIBRATION", value=7.2, unit="mm/s", ts=now)],
        ),
    )


def test_graph_builds():
    assert build_graph() is not None


def test_end_to_end_produces_alert_and_rca():
    final = run_graph(_make_event())
    assert final.get("alert_sent") is True
    assert final.get("jira_ticket_id")
    assert final.get("rca_hypothesis")
    assert final.get("shift_report")
    assert 0.0 <= final.get("confidence", 0) <= 1.0


def test_critic_loop_bounded():
    final = run_graph(_make_event())
    assert final.get("rca_iterations", 0) <= 3
