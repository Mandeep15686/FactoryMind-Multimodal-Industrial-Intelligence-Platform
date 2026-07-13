"""Grafana HTTP API tool — dashboard snapshots + annotation queries."""
from __future__ import annotations

import logging

from src.core.config import settings
from src.tools._base import tool

logger = logging.getLogger("factorymind.tools.grafana")


def snapshot_png(dashboard_uid: str) -> str:
    """Render a dashboard to PNG for embedding in shift reports; returns a URL."""
    if settings.grafana_api_key:
        try:  # pragma: no cover
            import httpx

            resp = httpx.post(
                f"{settings.grafana_url}/api/snapshots",
                json={"dashboard": {"uid": dashboard_uid}},
                headers={"Authorization": f"Bearer {settings.grafana_api_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("url", "")
        except Exception as exc:
            logger.warning("Grafana snapshot failed: %s", exc)
    return f"{settings.grafana_url}/render/d/{dashboard_uid}?mock=1"


def query_annotations(machine_id: str) -> list[dict]:
    """Fetch annotation history correlated to a machine."""
    if settings.grafana_api_key:
        try:  # pragma: no cover
            import httpx

            resp = httpx.get(
                f"{settings.grafana_url}/api/annotations",
                params={"tags": f"machine:{machine_id}"},
                headers={"Authorization": f"Bearer {settings.grafana_api_key}"},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning("Grafana annotations failed: %s", exc)
    return [{"time": "2026-07-11T06:00:00Z", "text": f"Shift start — {machine_id}", "tags": ["shift"]}]


grafana_snapshot = tool(snapshot_png)
grafana_annotations = tool(query_annotations)
