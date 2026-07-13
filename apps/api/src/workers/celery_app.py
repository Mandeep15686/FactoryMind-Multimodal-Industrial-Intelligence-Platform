"""Celery application + beat schedule.

Degrades to a stub when Celery is not installed so the tasks remain importable
(and callable synchronously) in a minimal environment.
"""
from __future__ import annotations

import logging

from src.core.config import settings

logger = logging.getLogger("factorymind.workers")

try:  # pragma: no cover - optional dep
    from celery import Celery

    celery_app = Celery(
        "factorymind",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )
    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        beat_schedule={
            "nightly-rag-refresh": {"task": "workers.rag_refresh.refresh_knowledge", "schedule": 24 * 3600},
            "nightly-evaluation": {"task": "workers.evaluation.run_nightly_eval", "schedule": 24 * 3600},
            "shift-report": {"task": "workers.shift_report.generate_shift_report", "schedule": 8 * 3600, "args": ("auto",)},
        },
    )
    _HAS_CELERY = True
except Exception:  # pragma: no cover

    class _StubTask:
        def __init__(self, fn):
            self._fn = fn

        def __call__(self, *a, **k):
            return self._fn(*a, **k)

        def delay(self, *a, **k):
            return self._fn(*a, **k)

    class _StubCelery:
        def task(self, *dargs, **dkw):
            def wrap(fn):
                return _StubTask(fn)

            # support both @celery_app.task and @celery_app.task(name=...)
            if dargs and callable(dargs[0]):
                return _StubTask(dargs[0])
            return wrap

    celery_app = _StubCelery()  # type: ignore[assignment]
    _HAS_CELERY = False
    logger.info("Celery unavailable — tasks run synchronously via stub")
