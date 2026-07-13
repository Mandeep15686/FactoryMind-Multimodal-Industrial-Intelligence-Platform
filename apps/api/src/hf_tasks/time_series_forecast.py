"""Time Series Forecasting — PatchTST / TimesFM. Sensor trajectory + RUL."""
from __future__ import annotations

from src.hf_tasks._client import hf_infer, is_mock, seeded_rng
from src.models.schemas import HealthState, SensorForecast

MODEL = "ibm-granite/granite-timeseries-patchtst"
_FAILURE_THRESHOLD = 100.0  # abstract health-metric units


def forecast(history: list[float], machine_id: str, horizon: int = 72) -> SensorForecast:
    """Forecast the next ``horizon`` steps and derive RUL + health state."""
    if not history:
        history = [50.0]

    preds: list[float] | None = None
    if not is_mock():
        result = hf_infer(MODEL, {"inputs": history, "parameters": {"prediction_length": horizon}}, task="time-series-forecasting")
        if result:
            preds = [float(x) for x in (result if isinstance(result, list) else result.get("predictions", []))][:horizon]

    if preds is None:
        # ── mock: linear trend from recent slope + bounded noise ──
        rng = seeded_rng("ts:" + machine_id)
        n = len(history)
        recent = history[-min(n, 24):]
        slope = (recent[-1] - recent[0]) / max(len(recent) - 1, 1)
        last = history[-1]
        preds = []
        for i in range(1, horizon + 1):
            last = last + slope + rng.gauss(0, 0.5)
            preds.append(round(last, 3))

    # ── RUL: hours until forecast crosses the failure threshold ──
    rul_hours: float | None = None
    for i, v in enumerate(preds):
        if v >= _FAILURE_THRESHOLD:
            rul_hours = float(i)
            break

    trend = "RISING" if preds[-1] > history[-1] + 1 else "FALLING" if preds[-1] < history[-1] - 1 else "STABLE"
    peak = max(preds)
    if peak >= _FAILURE_THRESHOLD or (rul_hours is not None and rul_hours < 24):
        health = HealthState.CRITICAL
    elif peak >= 0.8 * _FAILURE_THRESHOLD or trend == "RISING":
        health = HealthState.DEGRADED
    else:
        health = HealthState.HEALTHY

    return SensorForecast(
        machine_id=machine_id,
        horizon_hours=horizon,
        forecast=preds,
        rul_hours=rul_hours,
        health_state=health,
        trend=trend,
    )
