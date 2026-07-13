"""Dashboard + shift-report endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from src.core.security import CurrentPrincipal
from src.hf_tasks._client import seeded_rng

router = APIRouter(tags=["dashboard"])

_MACHINES = ["M05", "M12", "P07", "C22", "L03"]


@router.get("/dashboard/overview")
async def overview(principal: CurrentPrincipal) -> dict:
    return {
        "plant_id": principal.plant_id or "plant-demo",
        "machines_total": len(_MACHINES),
        "machines_healthy": 3,
        "machines_degraded": 1,
        "machines_critical": 1,
        "open_alerts": 2,
        "open_tickets": 4,
        "defect_rate_24h": 0.021,
        "avg_rca_confidence": 0.82,
    }


@router.get("/dashboard/machines")
async def machines_grid(principal: CurrentPrincipal) -> list[dict]:
    states = ["HEALTHY", "DEGRADED", "CRITICAL"]
    out = []
    for m in _MACHINES:
        rng = seeded_rng("dash:" + m)
        out.append(
            {
                "machine_id": m,
                "health_state": rng.choices(states, weights=[6, 3, 1])[0],
                "rul_hours": round(rng.uniform(12, 400), 1),
                "vibration": round(rng.uniform(2, 9), 2),
                "temperature_c": round(rng.uniform(40, 78), 1),
                "open_alerts": rng.randint(0, 3),
            }
        )
    return out


@router.get("/shifts/{shift_id}/report")
async def shift_report(shift_id: str, principal: CurrentPrincipal) -> dict:
    return {
        "shift_id": shift_id,
        "report_markdown": (
            "## Shift Summary\n\n"
            "3 machines healthy, 1 degraded (M05 coolant trend), 1 critical (M12 bearing).\n\n"
            "### Key Events\n- M12 CRITICAL bearing-wear anomaly → P0 ticket MAINT-1042.\n"
            "- P07 belt misalignment detected acoustically → P1 ticket MAINT-1043.\n\n"
            "### Recommendations\n- Replace SKF-22222-E-C3 on M12 before next shift.\n"
        ),
        "generated_by": "report_generation_agent",
    }
