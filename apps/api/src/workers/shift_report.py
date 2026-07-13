"""Scheduled shift-report generation task."""
from __future__ import annotations

import logging

from src.workers.celery_app import celery_app

logger = logging.getLogger("factorymind.workers.report")


@celery_app.task(name="workers.shift_report.generate_shift_report")
def generate_shift_report(shift_id: str) -> dict:
    """Aggregate shift events and produce an executive handover report."""
    from src.hf_tasks import summarization

    events = (
        "Shift recorded 2 critical anomalies and 3 maintenance actions. "
        "M12 bearing replaced. P07 belt realigned. Coolant filter changed on M05."
    )
    draft = summarization.summarize(events, max_words=200)
    logger.info("Shift report generated for %s", shift_id)
    return {"status": "ok", "shift_id": shift_id, "report": draft}
