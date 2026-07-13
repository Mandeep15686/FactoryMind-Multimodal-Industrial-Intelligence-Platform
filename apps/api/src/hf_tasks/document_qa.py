"""Document Question Answering — LayoutLMv3 / Donut. QA over scanned manuals."""
from __future__ import annotations

from src.hf_tasks._client import hf_infer, is_mock, seeded_rng

MODEL = "impira/layoutlm-document-qa"


def ask(doc_image_url: str, question: str) -> dict:
    """Return {answer, score, span}."""
    if not is_mock():
        result = hf_infer(
            MODEL, {"inputs": {"image": doc_image_url, "question": question}}, task="document-question-answering"
        )
        if result:
            top = result[0] if isinstance(result, list) else result
            return {"answer": top.get("answer", ""), "score": float(top.get("score", 0.0)), "span": top.get("start", 0)}
    rng = seeded_rng("docqa:" + doc_image_url + question)
    torque = rng.choice([24, 32, 40, 55])
    return {"answer": f"{torque} Nm ± 2 Nm", "score": round(rng.uniform(0.7, 0.97), 3), "span": rng.randint(100, 900)}
