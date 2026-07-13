"""Alert endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Query

from src.core.security import CurrentPrincipal

router = APIRouter(tags=["alerts"])

_ALERTS: dict[str, dict] = {
    "alert-1001": {"id": "alert-1001", "plant_id": "plant-demo", "machine_id": "M12", "severity": "CRITICAL", "status": "OPEN", "rca_id": "rca-1"},
    "alert-1002": {"id": "alert-1002", "plant_id": "plant-demo", "machine_id": "P07", "severity": "MAJOR", "status": "OPEN", "rca_id": "rca-2"},
}


@router.get("/alerts")
async def list_alerts(
    principal: CurrentPrincipal,
    plant_id: str | None = Query(None),
    severity: str | None = Query(None),
) -> list[dict]:
    alerts = list(_ALERTS.values())
    if plant_id:
        alerts = [a for a in alerts if a["plant_id"] == plant_id]
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    return alerts


@router.patch("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, principal: CurrentPrincipal) -> dict:
    from src.core.exceptions import NotFoundError

    alert = _ALERTS.get(alert_id)
    if not alert:
        raise NotFoundError(f"Alert {alert_id} not found")
    alert["status"] = "ACKNOWLEDGED"
    alert["acknowledged_by"] = principal.sub
    return alert


@router.get("/alerts/{alert_id}/rca")
async def get_alert_rca(alert_id: str, principal: CurrentPrincipal) -> dict:
    from src.core.exceptions import NotFoundError
    from src.routers.rca import get_rca_record

    alert = _ALERTS.get(alert_id)
    if not alert:
        raise NotFoundError(f"Alert {alert_id} not found")
    return get_rca_record(alert.get("rca_id", ""))
