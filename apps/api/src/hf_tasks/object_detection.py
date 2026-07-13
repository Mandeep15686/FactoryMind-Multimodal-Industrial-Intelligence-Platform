"""Object Detection — YOLO11 / RT-DETR-v2. Localizes surface defects."""
from __future__ import annotations

from src.hf_tasks._client import fetch_bytes, hf_infer, is_mock, seeded_rng

MODEL = "Ultralytics/YOLO11"
_LABELS = ["crack", "scratch", "contamination", "misalignment"]


def detect_objects(image_url: str) -> list[dict]:
    """Return a list of detections: {label, score, box:{x,y,w,h}}."""
    if not is_mock():
        payload = fetch_bytes(image_url)
        if payload is not None:
            result = hf_infer(MODEL, payload, task="object-detection")
            if result:
                return [
                    {
                        "label": d.get("label", "defect"),
                        "score": float(d.get("score", 0.0)),
                        "box": {
                            "x": d["box"]["xmin"],
                            "y": d["box"]["ymin"],
                            "w": d["box"]["xmax"] - d["box"]["xmin"],
                            "h": d["box"]["ymax"] - d["box"]["ymin"],
                        },
                    }
                    for d in result
                ]
    # ── mock ──
    rng = seeded_rng(image_url)
    n = rng.randint(0, 3)
    dets = []
    for _ in range(n):
        dets.append(
            {
                "label": rng.choice(_LABELS),
                "score": round(rng.uniform(0.55, 0.98), 3),
                "box": {
                    "x": rng.randint(0, 1600),
                    "y": rng.randint(0, 900),
                    "w": rng.randint(20, 200),
                    "h": rng.randint(20, 200),
                },
            }
        )
    return dets
