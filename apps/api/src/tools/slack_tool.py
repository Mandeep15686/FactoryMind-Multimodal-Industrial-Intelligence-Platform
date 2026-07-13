"""Slack Web API tool — alerts + interactive approval requests."""
from __future__ import annotations

import hashlib
import logging

from src.core.config import settings
from src.tools._base import tool

logger = logging.getLogger("factorymind.tools.slack")

_EMOJI = {"CRITICAL": ":rotating_light:", "MAJOR": ":warning:", "INFO": ":information_source:"}


def notify(channel: str, text: str, severity: str = "INFO", attachments: list | None = None) -> bool:
    """Post a message to a Slack channel."""
    emoji = _EMOJI.get(severity, "")
    message = f"{emoji} {text}".strip()
    if settings.slack_bot_token:
        try:  # pragma: no cover
            from slack_sdk import WebClient

            client = WebClient(token=settings.slack_bot_token)
            client.chat_postMessage(channel=channel, text=message, attachments=attachments)
            return True
        except Exception as exc:
            logger.warning("Slack notify failed: %s", exc)
            return False
    logger.info("MOCK Slack[%s] %s", channel, message)
    return True


def approval_request(channel: str, text: str) -> str:
    """Post an interactive approval request; returns the message timestamp/id."""
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": text}},
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": "Approve"}, "style": "primary", "value": "approve"},
                {"type": "button", "text": {"type": "plain_text", "text": "Reject"}, "style": "danger", "value": "reject"},
            ],
        },
    ]
    if settings.slack_bot_token:
        try:  # pragma: no cover
            from slack_sdk import WebClient

            client = WebClient(token=settings.slack_bot_token)
            resp = client.chat_postMessage(channel=channel, text=text, blocks=blocks)
            return resp["ts"]
        except Exception as exc:
            logger.warning("Slack approval failed: %s", exc)
    ts = hashlib.md5(text.encode()).hexdigest()[:12]
    logger.info("MOCK Slack approval[%s] ts=%s", channel, ts)
    return ts


slack_notify = tool(notify)
slack_approval_request = tool(approval_request)
