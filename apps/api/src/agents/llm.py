"""LLM helper — Claude (primary) with a deterministic offline mock.

All agents call through here so tracing, cost accounting, and the mock fallback
live in one place. When ``settings.anthropic_api_key`` is empty the mock returns
plausible structured output so the whole graph runs offline.
"""
from __future__ import annotations

import json
import logging

from src.core.config import settings
from src.core.observability import record_llm_cost

logger = logging.getLogger("factorymind.llm")

# Rough Claude Sonnet pricing (USD per token) — illustrative.
_COST_IN = 3.0 / 1_000_000
_COST_OUT = 15.0 / 1_000_000


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    cost = tokens_in * _COST_IN + tokens_out * _COST_OUT
    record_llm_cost(model, cost)
    return round(cost, 6)


def _mock_completion(system: str, user: str) -> str:
    return (
        "Based on the multimodal signals and retrieved maintenance knowledge, the most "
        "probable root cause is drive-end bearing wear driven by lubrication starvation, "
        "consistent with the rising vibration trend and the acoustic anomaly signature."
    )


def call_llm(system: str, user: str, model: str | None = None, tools: list | None = None) -> str:
    """Return a free-text completion."""
    model = model or settings.primary_llm_model
    if settings.anthropic_api_key:
        try:  # pragma: no cover - requires network + key
            import anthropic

            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            resp = client.messages.create(
                model=model,
                max_tokens=settings.llm_max_tokens,
                temperature=settings.llm_temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
            estimate_cost(model, resp.usage.input_tokens, resp.usage.output_tokens)
            return text
        except Exception as exc:
            logger.warning("LLM call failed, using mock: %s", exc)
    estimate_cost(model, len(user.split()), 120)
    return _mock_completion(system, user)


def call_llm_json(system: str, user: str, schema_hint: dict) -> dict:
    """Return a parsed JSON object matching ``schema_hint`` keys.

    Falls back to a deterministic mock object shaped like ``schema_hint``. The
    mock is *context-aware* — it derives its hypothesis from the retrieved
    knowledge embedded in ``user`` so grounding/faithfulness evaluation is
    meaningful rather than a fixed string.
    """
    model = settings.primary_llm_model
    if settings.anthropic_api_key:
        try:  # pragma: no cover
            text = call_llm(
                system + "\nRespond ONLY with a valid JSON object.",
                user + f"\n\nJSON schema (keys): {list(schema_hint.keys())}",
                model=model,
            )
            start, end = text.find("{"), text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start : end + 1])
        except Exception as exc:
            logger.warning("LLM JSON parse failed, using mock: %s", exc)
    estimate_cost(model, len(user.split()), 200)
    return _mock_rca(schema_hint, context=user)


# Failure-mode templates keyed by signal keywords found in the retrieved context.
_FAILURE_TEMPLATES = [
    {
        "keys": ("belt", "misalignment", "sheave", "tension"),
        "hypothesis": "Belt misalignment causing accelerated sheave wear, consistent with the "
        "800 Hz-1.2 kHz acoustic signature.",
        "cause": "Belt misalignment / improper tension",
        "recommendations": [
            "Laser-align the belt to within 0.5 mm",
            "Re-tension the belt to 55 Nm",
        ],
    },
    {
        "keys": ("coolant", "pump", "cavitation", "filter", "contamination", "filtration"),
        "hypothesis": "Coolant filtration breakdown and pump cavitation driving elevated coolant "
        "temperature and surface contamination.",
        "cause": "Coolant filtration breakdown / pump cavitation",
        "recommendations": [
            "Replace the 50-micron coolant filter",
            "Inspect the coolant pump impeller for cavitation damage",
        ],
    },
    {
        "keys": ("bearing", "lubrication", "grease", "vibration", "overheating"),
        "hypothesis": "Drive-end bearing wear caused by lubrication starvation, leading to elevated "
        "vibration and a rising thermal trend approaching the failure threshold.",
        "cause": "Lubrication starvation at the drive-end bearing",
        "recommendations": [
            "Replace bearing SKF-22222-E-C3 and verify seal integrity",
            "Re-grease to the OEM torque spec of 40 Nm",
        ],
    },
]


def _pick_template(context: str) -> dict:
    ctx = context.lower()
    best = _FAILURE_TEMPLATES[-1]
    best_hits = -1
    for tmpl in _FAILURE_TEMPLATES:
        hits = sum(1 for k in tmpl["keys"] if k in ctx)
        if hits > best_hits:
            best_hits, best = hits, tmpl
    return best


def _mock_rca(schema_hint: dict, context: str = "") -> dict:
    """Deterministic, context-aware RCA-shaped mock (5-Whys).

    Selects the failure-mode template whose signal keywords best match the
    retrieved knowledge in ``context`` so that generated claims are grounded.
    """
    tmpl = _pick_template(context)
    base = {
        "hypothesis": tmpl["hypothesis"],
        "root_causes": [
            {"cause": tmpl["cause"], "probability": 0.66, "evidence": tmpl["recommendations"]},
        ],
        "recommendations": tmpl["recommendations"],
        "confidence": 0.82,
        "evidence": [
            "Signal deviates from the learned machine baseline",
            "Retrieved maintenance knowledge corroborates the failure mode",
        ],
    }
    return {k: base.get(k, base) for k in schema_hint} if schema_hint else base
