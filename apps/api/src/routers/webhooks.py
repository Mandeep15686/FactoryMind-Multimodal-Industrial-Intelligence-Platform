"""Inbound webhooks — Jira status sync + Slack interactive callbacks."""
from __future__ import annotations

import hashlib
import hmac
import logging

from fastapi import APIRouter, Request

from src.core.config import settings

logger = logging.getLogger("factorymind.webhooks")
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/jira")
async def jira_webhook(request: Request) -> dict:
    payload = await request.json()
    issue = payload.get("issue", {})
    key = issue.get("key")
    status = issue.get("fields", {}).get("status", {}).get("name")
    logger.info("Jira webhook: %s -> %s", key, status)
    return {"received": True, "ticket": key, "status": status}


@router.post("/slack/actions")
async def slack_actions(request: Request) -> dict:
    raw = await request.body()
    if settings.slack_signing_secret:
        ts = request.headers.get("X-Slack-Request-Timestamp", "")
        sig = request.headers.get("X-Slack-Signature", "")
        basestring = f"v0:{ts}:{raw.decode(errors='ignore')}"
        expected = "v0=" + hmac.new(settings.slack_signing_secret.encode(), basestring.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            logger.warning("Slack signature mismatch (accepted in dev)")
    # In production: resume the interrupted LangGraph run with the approval result.
    return {"received": True}
