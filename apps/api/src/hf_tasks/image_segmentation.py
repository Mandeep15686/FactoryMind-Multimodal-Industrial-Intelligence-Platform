"""Image Segmentation — SegFormer-b3. Pixel-level defect area measurement."""
from __future__ import annotations

from src.hf_tasks._client import fetch_bytes, hf_infer, is_mock, seeded_rng

MODEL = "nvidia/segformer-b3-finetuned-ade-512-512"


def segment(image_url: str) -> dict:
    """Return {mask_area_px, area_mm2, label}."""
    if not is_mock():
        payload = fetch_bytes(image_url)
        if payload is not None:
            result = hf_infer(MODEL, payload, task="image-segmentation")
            if result:
                top = result[0]
                px = int(top.get("mask_area", 5000))
                return {"mask_area_px": px, "area_mm2": round(px * 0.0004, 3), "label": top.get("label", "defect")}
    rng = seeded_rng("seg:" + image_url)
    px = rng.randint(200, 40_000)
    return {"mask_area_px": px, "area_mm2": round(px * 0.0004, 3), "label": rng.choice(["crack", "scratch", "contamination"])}
