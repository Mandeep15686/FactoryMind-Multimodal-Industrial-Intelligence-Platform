"""Audio Classification — AST / PANNs (CNN14). Machine acoustic anomalies."""
from __future__ import annotations

from src.hf_tasks._client import fetch_bytes, hf_infer, is_mock, seeded_rng

MODEL = "MIT/ast-finetuned-audioset-10-10-0.4593"
_CLASSES = ["normal", "bearing_wear", "belt_misalignment", "lubrication_fault", "loose_component"]


def classify_audio(audio_url: str) -> dict:
    """Return {anomaly_class, score, baseline_deviation}."""
    if not is_mock():
        payload = fetch_bytes(audio_url)
        if payload is not None:
            result = hf_infer(MODEL, payload, task="audio-classification")
            if result:
                top = result[0]
                return {
                    "anomaly_class": top.get("label", "normal"),
                    "score": float(top.get("score", 0.0)),
                    "baseline_deviation": round(abs(float(top.get("score", 0.0)) - 0.5) * 2, 3),
                }
    rng = seeded_rng("aud:" + audio_url)
    cls = rng.choices(_CLASSES, weights=[6, 2, 1, 1, 1])[0]
    score = round(rng.uniform(0.6, 0.99), 3)
    dev = 0.0 if cls == "normal" else round(rng.uniform(0.3, 0.95), 3)
    return {"anomaly_class": cls, "score": score, "baseline_deviation": dev}
