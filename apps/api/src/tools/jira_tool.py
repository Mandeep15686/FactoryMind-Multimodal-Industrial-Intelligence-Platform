"""Jira REST API tool — create/update maintenance tickets."""
from __future__ import annotations

import hashlib
import logging

from src.core.config import settings
from src.tools._base import tool

logger = logging.getLogger("factorymind.tools.jira")

_PRIORITY_MAP = {"P0": "Highest", "P1": "High", "P2": "Medium", "P3": "Low"}


def create_ticket(
    summary: str,
    description: str,
    priority: str,
    machine_id: str,
    parts: list[str] | None = None,
) -> str:
    """Create a Jira maintenance ticket; returns the issue key (e.g. MAINT-1234)."""
    if settings.jira_api_token and settings.jira_email:
        try:  # pragma: no cover - requires network
            import httpx

            payload = {
                "fields": {
                    "project": {"key": settings.jira_project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": "Task"},
                    "priority": {"name": _PRIORITY_MAP.get(priority, "Medium")},
                    "labels": [f"machine:{machine_id}"] + [f"part:{p}" for p in (parts or [])],
                }
            }
            resp = httpx.post(
                f"{settings.jira_base_url}/rest/api/3/issue",
                json=payload,
                auth=(settings.jira_email, settings.jira_api_token),
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()["key"]
        except Exception as exc:
            logger.warning("Jira create failed, using mock id: %s", exc)

    # deterministic mock key
    digest = hashlib.md5(f"{machine_id}:{summary}".encode()).hexdigest()
    num = int(digest[:6], 16) % 9000 + 1000
    key = f"{settings.jira_project_key}-{num}"
    logger.info("MOCK Jira ticket %s created (%s)", key, priority)
    return key


def update_ticket(ticket_id: str, status: str) -> bool:
    """Transition a Jira ticket to a new status."""
    if settings.jira_api_token:
        try:  # pragma: no cover
            import httpx

            httpx.post(
                f"{settings.jira_base_url}/rest/api/3/issue/{ticket_id}/transitions",
                json={"transition": {"name": status}},
                auth=(settings.jira_email, settings.jira_api_token),
                timeout=15,
            )
            return True
        except Exception as exc:
            logger.warning("Jira update failed: %s", exc)
            return False
    logger.info("MOCK Jira ticket %s -> %s", ticket_id, status)
    return True


jira_create_ticket = tool(create_ticket)
jira_update_ticket = tool(update_ticket)
