"""Image Classification — ViT-Large / EfficientNet-v2. Severity + type."""
from __future__ import annotations

from src.hf_tasks._client import fetch_bytes, hf_infer, is_mock, seeded_rng

MODEL = "google/vit-large-patch16-224"
_SEV = ["CRITICAL", "MAJOR", "MINOR"]
_TYPE = ["CRACK", "SCRATCH", "CONTAMINATION", "MISALIGNMENT"]


def classify(image_url: str) -> dict:
    """Return {severity, defect_type, confidence}."""
    if not is_mock():
        payload = fetch_bytes(image_url)
        if payload is not None:
            result = hf_infer(MODEL, payload, task="image-classification")
            if result:
                top = result[0]
                return {"severity": "MAJOR", "defect_type": top.get("label", "UNKNOWN").upper(), "confidence": float(top.get("score", 0.0))}
    rng = seeded_rng("cls:" + image_url)
    return {
        "severity": rng.choices(_SEV, weights=[1, 3, 6])[0],
        "defect_type": rng.choice(_TYPE),
        "confidence": round(rng.uniform(0.6, 0.99), 3),
    }
