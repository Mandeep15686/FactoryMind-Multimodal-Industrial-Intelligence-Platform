"""Visual Inspection Agent — HF vision pipeline → structured Defect list."""
from __future__ import annotations

from src.agents.state import FactoryMindState
from src.core.observability import trace_span
from src.hf_tasks import (
    image_classification,
    image_feature_extraction,
    image_segmentation,
    object_detection,
    zero_shot_image_cls,
)
from src.models.schemas import BoundingBox, Defect, DefectType, Severity

_SEV_ORDER = {Severity.NONE: 0, Severity.MINOR: 1, Severity.MAJOR: 2, Severity.CRITICAL: 3}
_KNOWN = ["crack", "scratch", "contamination", "misalignment"]


def visual_inspection_node(state: FactoryMindState) -> dict:
    with trace_span("visual_inspection", machine_id=state.get("machine_id")):
        defects: list[Defect] = []
        for frame in state.get("frames", []):
            url = getattr(frame, "s3_url", None) or (frame.get("s3_url") if isinstance(frame, dict) else None)
            if not url:
                continue
            for det in object_detection.detect_objects(url):
                seg = image_segmentation.segment(url)
                cls = image_classification.classify(url)
                embedding = image_feature_extraction.extract_features(url)

                # Zero-shot novelty check: flag defects unlike known classes.
                zs = zero_shot_image_cls.classify_zero_shot(url, _KNOWN + ["unknown defect"])
                dtype = _map_type(cls["defect_type"], zs)

                box = det["box"]
                defects.append(
                    Defect(
                        defect_type=dtype,
                        severity=Severity(cls["severity"]),
                        confidence=round((det["score"] + cls["confidence"]) / 2, 3),
                        bbox=BoundingBox(x=box["x"], y=box["y"], w=box["w"], h=box["h"], image_url=url),
                        area_mm2=seg["area_mm2"],
                        description=f"{dtype.value.title()} detected ({seg['area_mm2']} mm²)",
                        visual_embedding=embedding,
                    )
                )

        severity = _max_severity(defects)
        return {"defects": defects, "defect_severity": severity.value}


def _map_type(cls_type: str, zero_shot: list[dict]) -> DefectType:
    top = zero_shot[0]["label"] if zero_shot else ""
    if "unknown" in top:
        return DefectType.UNKNOWN
    try:
        return DefectType(cls_type)
    except ValueError:
        return DefectType.UNKNOWN


def _max_severity(defects: list[Defect]) -> Severity:
    if not defects:
        return Severity.NONE
    return max((d.severity for d in defects), key=lambda s: _SEV_ORDER[s])
