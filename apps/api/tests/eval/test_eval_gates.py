"""Evaluation-gate smoke tests (thresholds from blueprint Section 17)."""
from __future__ import annotations

from src.workers.evaluation import run_nightly_eval


def test_eval_metrics_meet_gate():
    result = run_nightly_eval()
    m = result["metrics"]
    assert m["faithfulness"] >= 0.85
    assert m["hallucination_rate"] < 0.05
    assert result["pass_gate"] is True
