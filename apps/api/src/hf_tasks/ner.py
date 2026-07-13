"""Token Classification (NER) — BERT/RoBERTa. Extracts maintenance entities."""
from __future__ import annotations

import re

from src.hf_tasks._client import hf_infer, is_mock
from src.models.schemas import Entity

MODEL = "dslim/bert-base-NER"

_PATTERNS = {
    "MACHINE_ID": re.compile(r"\b[MP]\d{2,4}\b"),
    "PART_NUMBER": re.compile(r"\b[A-Z]{2,4}-\d{3,6}(?:-[A-Z0-9]+)*\b"),
    "ERROR_CODE": re.compile(r"\bE-?\d{2,4}\b"),
    "FAILURE_MODE": re.compile(r"\b(?:bearing wear|belt (?:wear|misalignment)|overheating|lubrication fault|crack)\b", re.I),
    "CORRECTIVE_ACTION": re.compile(r"\b(?:replaced?|inspect(?:ed)?|torque(?:d)?|realign(?:ed)?|lubricate(?:d)?)\b", re.I),
}


def extract_entities(text: str) -> list[Entity]:
    """Return tagged entities from maintenance/technician text."""
    if not is_mock():
        result = hf_infer(MODEL, {"inputs": text}, task="token-classification")
        if result:
            return [
                Entity(
                    label=r.get("entity_group", r.get("entity", "MISC")),
                    text=r.get("word", ""),
                    start=int(r.get("start", 0)),
                    end=int(r.get("end", 0)),
                    score=float(r.get("score", 1.0)),
                )
                for r in result
            ]
    entities: list[Entity] = []
    for label, pat in _PATTERNS.items():
        for m in pat.finditer(text):
            entities.append(Entity(label=label, text=m.group(), start=m.start(), end=m.end(), score=1.0))
    return entities
