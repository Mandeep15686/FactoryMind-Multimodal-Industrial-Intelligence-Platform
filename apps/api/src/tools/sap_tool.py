"""SAP ERP tool — spare-parts inventory + maintenance schedule lookups."""
from __future__ import annotations

import logging

from src.core.config import settings
from src.hf_tasks._client import seeded_rng
from src.tools._base import tool

logger = logging.getLogger("factorymind.tools.sap")


def check_inventory(parts: list[str]) -> dict[str, bool]:
    """Return per-part availability from SAP inventory."""
    if settings.sap_api_key:
        try:  # pragma: no cover
            import httpx

            resp = httpx.post(
                f"{settings.sap_base_url}/inventory/check",
                json={"parts": parts},
                headers={"APIKey": settings.sap_api_key},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning("SAP inventory check failed: %s", exc)
    # deterministic mock: most parts in stock
    out = {}
    for p in parts:
        out[p] = seeded_rng("inv:" + p).random() > 0.15
    logger.info("MOCK SAP inventory %s", out)
    return out


def get_maintenance_schedule(machine_id: str) -> dict:
    """Return the current planned-maintenance window for a machine."""
    if settings.sap_api_key:
        try:  # pragma: no cover
            import httpx

            resp = httpx.get(
                f"{settings.sap_base_url}/maintenance/schedule/{machine_id}",
                headers={"APIKey": settings.sap_api_key},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            logger.warning("SAP schedule lookup failed: %s", exc)
    return {"machine_id": machine_id, "next_window": "2026-07-18T22:00:00Z", "technicians_free": True}


sap_check_inventory = tool(check_inventory)
sap_get_schedule = tool(get_maintenance_schedule)
