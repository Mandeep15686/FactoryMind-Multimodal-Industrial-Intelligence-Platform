"""PagerDuty Events API v2 tool — trigger P0 incidents."""
from __future__ import annotations

import hashlib
import logging

from src.core.config import settings
from src.tools._base import tool

logger = logging.getLogger("factorymind.tools.pagerduty")


def trigger_incident(summary: str, severity: str, machine_id: str) -> str:
    """Trigger a PagerDuty incident; returns the dedup key."""
    dedup_key = hashlib.md5(f"{machine_id}:{summary}".encode()).hexdigest()
    if settings.pagerduty_routing_key:
        try:  # pragma: no cover
            import httpx

            payload = {
                "routing_key": settings.pagerduty_routing_key,
                "event_action": "trigger",
                "dedup_key": dedup_key,
                "payload": {
                    "summary": summary,
                    "severity": severity,
                    "source": f"factorymind/{machine_id}",
                    "component": machine_id,
                },
            }
            resp = httpx.post("https://events.pagerduty.com/v2/enqueue", json=payload, timeout=15)
            resp.raise_for_status()
            return resp.json().get("dedup_key", dedup_key)
        except Exception as exc:
            logger.warning("PagerDuty trigger failed: %s", exc)
    logger.info("MOCK PagerDuty incident dedup=%s severity=%s", dedup_key, severity)
    return dedup_key


pagerduty_trigger = tool(trigger_incident)
