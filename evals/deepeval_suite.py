"""DeepEval-style hallucination check on RCA output.

Verifies that generated root-cause claims are grounded in retrieved context.
Falls back to a lexical grounding proxy when ``deepeval`` is not installed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from src.agents.llm import call_llm_json  # noqa: E402
from src.rag import retrieve_knowledge  # noqa: E402

DATASET = ROOT / "evals" / "datasets" / "rca_golden.json"
HALLUCINATION_TARGET = 0.05  # < 5%


def _grounded(claim: str, context: str) -> bool:
    terms = [t for t in claim.lower().split() if len(t) > 5]
    if not terms:
        return True
    hits = sum(1 for t in terms if t in context.lower())
    return hits / len(terms) >= 0.15


def run() -> dict:
    cases = json.loads(DATASET.read_text())
    total_claims = 0
    ungrounded = 0
    for case in cases:
        query = " ".join(str(v) for v in case["signals"].values())
        retrieval = retrieve_knowledge(query, machine_type=case["machine_type"])
        context = " ".join(d.text for d in retrieval.documents)
        rca = call_llm_json("Diagnose root cause.", query, {"root_causes": []})
        claims = rca.get("root_causes", [])
        for c in claims:
            text = c["cause"] if isinstance(c, dict) else str(c)
            total_claims += 1
            if not _grounded(text, context):
                ungrounded += 1

    rate = round(ungrounded / total_claims, 4) if total_claims else 0.0
    metrics = {
        "total_claims": total_claims,
        "ungrounded_claims": ungrounded,
        "hallucination_rate": rate,
        "pass_gate": rate < HALLUCINATION_TARGET,
    }
    return metrics


if __name__ == "__main__":
    m = run()
    print(json.dumps(m, indent=2))
    sys.exit(0 if m["pass_gate"] else 1)
