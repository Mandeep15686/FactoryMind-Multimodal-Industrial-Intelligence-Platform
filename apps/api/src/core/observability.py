"""Observability: OpenTelemetry tracing, Langfuse LLM tracing, Prometheus metrics.

All three degrade gracefully when their backends / keys are absent so the
service runs in local dev without an OTEL collector or Langfuse instance.
"""
from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Iterator

from src.core.config import settings

logger = logging.getLogger("factorymind")

# ── Prometheus metrics (no-op if client missing) ────────────
try:
    from prometheus_client import Counter, Histogram

    RCA_DURATION = Histogram(
        "factorymind_rca_duration_seconds", "End-to-end RCA duration", ["plant_id"]
    )
    LLM_COST = Counter(
        "factorymind_llm_cost_total", "Cumulative LLM cost in USD", ["model"]
    )
    DEFECTS_DETECTED = Counter(
        "factorymind_defects_detected_total", "Defects detected", ["severity"]
    )
    DEFECT_LATENCY = Histogram(
        "factorymind_defect_detection_latency_ms", "Defect detection latency (ms)"
    )
    _PROM = True
except Exception:  # pragma: no cover
    _PROM = False
    RCA_DURATION = LLM_COST = DEFECTS_DETECTED = DEFECT_LATENCY = None  # type: ignore


# ── Langfuse client (optional) ──────────────────────────────
def get_langfuse():  # pragma: no cover
    if not settings.langfuse_secret_key:
        return None
    try:
        from langfuse import Langfuse

        return Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
    except Exception:
        return None


def configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format='{"ts":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
    )


def configure_tracing(app) -> None:  # noqa: ANN001
    """Instrument FastAPI with OpenTelemetry if the exporter is reachable."""
    try:  # pragma: no cover
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("OpenTelemetry instrumentation enabled")
    except Exception:
        logger.info("OTEL not available — skipping tracing instrumentation")


@contextmanager
def trace_span(name: str, **attrs) -> Iterator[dict]:
    """Lightweight span used to time agent steps and emit metrics."""
    start = time.perf_counter()
    ctx = {"name": name, **attrs}
    try:
        yield ctx
    finally:
        ctx["duration_ms"] = round((time.perf_counter() - start) * 1000, 2)
        logger.info(f"span={name} attrs={ctx}")


def record_llm_cost(model: str, cost_usd: float) -> None:
    if _PROM and LLM_COST is not None:
        LLM_COST.labels(model=model).inc(cost_usd)
