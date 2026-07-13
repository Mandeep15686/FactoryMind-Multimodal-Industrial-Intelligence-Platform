"""Celery background workers: RAG refresh, shift reports, evaluation."""

from src.workers.celery_app import celery_app  # noqa: F401

__all__ = ["celery_app"]
