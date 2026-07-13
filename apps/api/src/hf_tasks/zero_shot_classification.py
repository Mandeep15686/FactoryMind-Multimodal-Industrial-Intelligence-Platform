"""Zero-Shot Classification — DeBERTa-v3-large-zeroshot. Dynamic taxonomies."""
from __future__ import annotations

from src.hf_tasks._client import hf_infer, is_mock, seeded_rng

MODEL = "MoritzLaurer/deberta-v3-large-zeroshot-v2.0"


def classify_text(text: str, labels: list[str]) -> list[dict]:
    """Return labels ranked by probability: [{label, score}]."""
    if not is_mock():
        result = hf_infer(
            MODEL,
            {"inputs": text, "parameters": {"candidate_labels": labels, "multi_label": False}},
            task="zero-shot-classification",
        )
        if result:
            return [
                {"label": lbl, "score": float(sc)}
                for lbl, sc in zip(result["labels"], result["scores"])
            ]
    rng = seeded_rng("zsc:" + text + "|".join(labels))
    raw = [(lbl, rng.uniform(0.01, 1.0)) for lbl in labels]
    total = sum(s for _, s in raw) or 1.0
    scored = sorted(({"label": lbl, "score": round(s / total, 4)} for lbl, s in raw), key=lambda x: x["score"], reverse=True)
    return scored
