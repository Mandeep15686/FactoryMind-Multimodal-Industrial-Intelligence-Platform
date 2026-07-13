"""Sensor Analysis Agent — time-series forecasting → RUL + health state."""
from __future__ import annotations

from src.agents.state import FactoryMindState
from src.core.observability import trace_span
from src.hf_tasks import time_series_forecast
from src.hf_tasks._client import seeded_rng


def sensor_analysis_node(state: FactoryMindState) -> dict:
    machine_id = state.get("machine_id", "unknown")
    with trace_span("sensor_analysis", machine_id=machine_id):
        history = _build_history(state)
        forecast = time_series_forecast.forecast(history, machine_id=machine_id)
        return {"rul_hours": forecast.rul_hours, "health_state": forecast.health_state.value}


def _build_history(state: FactoryMindState) -> list[float]:
    """Assemble a 7-day health-metric history from the sensor snapshot.

    In production this queries TimescaleDB for the rolling window; here we
    synthesize a deterministic series seeded by machine_id, anchored on the
    latest live reading when one is present.
    """
    snapshot = state.get("sensor_snapshot")
    rng = seeded_rng("hist:" + state.get("machine_id", "x"))
    base = 45.0
    if snapshot is not None:
        readings = getattr(snapshot, "readings", None) or []
        if readings:
            base = float(getattr(readings[-1], "value", 45.0))
    series = []
    val = base
    for _ in range(7 * 24):  # 7 days hourly
        val = max(0.0, val + rng.gauss(0.05, 0.8))
        series.append(round(val, 3))
    return series
