"""Feedback Agent — captures technician verdicts, triggers nightly evaluation."""
from __future__ import annotations

import logging

from src.agents.state import FactoryMindState
from src.core.observability import trace_span

logger = logging.getLogger("factorymind.feedback")


def feedback_node(state: FactoryMindState) -> dict:
    """Persist the completed event for later feedback + evaluation curation.

    The technician verdict (CORRECT/PARTIAL/WRONG) arrives asynchronously via the
    /rca/{id}/feedback endpoint; this node registers the event so the nightly
    LangSmith/Langfuse evaluation pipeline can pick it up.
    """
    with trace_span("feedback", event_id=state.get("event_id")):
        logger.info(
            "event_complete id=%s machine=%s alert_sent=%s ticket=%s confidence=%s",
            state.get("event_id"),
            state.get("machine_id"),
            state.get("alert_sent"),
            state.get("jira_ticket_id"),
            state.get("confidence"),
        )
        # Enqueue for evaluation (Celery task in production).
        try:
            from src.workers.evaluation import run_nightly_eval

            run_nightly_eval.delay()  # type: ignore[attr-defined]
        except Exception:
            pass
        return {}
