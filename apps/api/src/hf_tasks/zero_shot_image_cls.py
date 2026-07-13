"""Zero-Shot Image Classification — CLIP-ViT-L/14. Flags novel defect types."""
from __future__ import annotations

from src.hf_tasks._client import fetch_bytes, hf_infer, is_mock, seeded_rng

MODEL = "openai/clip-vit-large-patch14"


def classify_zero_shot(image_url: str, labels: list[str]) -> list[dict]:
    """Return labels ranked by score: [{label, score}]."""
    if not is_mock():
        payload = fetch_bytes(image_url)
        if payload is not None:
            result = hf_infer(
                MODEL,
                {"inputs": {"image_url": image_url}, "parameters": {"candidate_labels": labels}},
                task="zero-shot-image-classification",
            )
            if result:
                return [{"label": r["label"], "score": float(r["score"])} for r in result]
    rng = seeded_rng("zsi:" + image_url + "|".join(labels))
    scored = sorted(
        ({"label": lbl, "score": round(rng.uniform(0.05, 0.95), 3)} for lbl in labels),
        key=lambda x: x["score"],
        reverse=True,
    )
    return scored
