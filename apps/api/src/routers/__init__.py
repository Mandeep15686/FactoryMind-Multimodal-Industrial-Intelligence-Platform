"""Router aggregation.

``main.py`` mounts ``api_router`` at ``settings.api_v1_prefix`` (/api/v1), so
sub-routers use bare paths like ``/alerts``. ``ws_router`` and ``webhook_router``
are mounted at the app root.
"""
from fastapi import APIRouter

from src.routers import (
    alerts,
    dashboard,
    inspections,
    knowledge,
    maintenance,
    models,
    rca,
    webhooks,
    ws,
)

# ── /api/v1/* ──
api_router = APIRouter()
api_router.include_router(inspections.router)
api_router.include_router(alerts.router)
api_router.include_router(rca.router)
api_router.include_router(maintenance.router)
api_router.include_router(knowledge.router)
api_router.include_router(dashboard.router)
api_router.include_router(models.router)

# ── root-mounted ──
ws_router = ws.router
webhook_router = webhooks.router

__all__ = ["api_router", "ws_router", "webhook_router"]
