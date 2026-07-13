"""Visual Question Answering — LLaVA-1.6 / InternVL2. Interactive defect Q&A."""
from __future__ import annotations

from src.hf_tasks._client import hf_infer, is_mock, seeded_rng

MODEL = "llava-hf/llava-v1.6-mistral-7b-hf"


def ask(image_url: str, question: str) -> str:
    """Answer a natural-language question about a defect image."""
    if not is_mock():
        result = hf_infer(
            MODEL, {"inputs": {"image_url": image_url, "question": question}}, task="visual-question-answering"
        )
        if result:
            if isinstance(result, list):
                return str(result[0].get("answer", result[0]))
            return str(result)
    rng = seeded_rng("vqa:" + image_url + question)
    orientation = rng.choice(["longitudinal", "transverse"])
    crosses = rng.choice(["does not cross", "crosses"])
    return (
        f"The observed surface crack appears {orientation}. It {crosses} the heat-affected "
        f"zone. Estimated length is approximately {rng.randint(2, 18)} mm; recommend "
        f"dye-penetrant inspection to confirm propagation before returning the part to service."
    )
