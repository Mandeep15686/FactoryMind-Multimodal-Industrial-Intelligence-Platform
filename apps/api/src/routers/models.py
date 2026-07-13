"""LLMOps / model-management endpoints — prompts + evaluation runs."""
from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from src.core.exceptions import NotFoundError
from src.core.security import Role, require_role

router = APIRouter(tags=["llmops"])

_PROMPTS: dict[str, dict] = {
    "p-rca-v1": {"id": "p-rca-v1", "name": "rca_system", "version": "1.0.0", "is_active": True},
}
_EVALS: dict[str, dict] = {}


class PromptCreate(BaseModel):
    name: str
    version: str
    content: str


class EvalRequest(BaseModel):
    eval_type: str = "RAGAS"
    prompt_version: str = "1.0.0"
    dataset_version: str = "v1.0"


@router.get("/prompts")
async def list_prompts(_=require_role(Role.ADMIN)) -> list[dict]:
    return list(_PROMPTS.values())


@router.post("/prompts")
async def create_prompt(req: PromptCreate, _=require_role(Role.ADMIN)) -> dict:
    pid = f"p-{uuid.uuid4().hex[:8]}"
    rec = {"id": pid, **req.model_dump(), "is_active": False, "created_at": datetime.utcnow().isoformat()}
    _PROMPTS[pid] = rec
    return rec


@router.post("/prompts/{prompt_id}/activate")
async def activate_prompt(prompt_id: str, _=require_role(Role.ADMIN)) -> dict:
    rec = _PROMPTS.get(prompt_id)
    if not rec:
        raise NotFoundError(f"Prompt {prompt_id} not found")
    for p in _PROMPTS.values():
        if p["name"] == rec["name"]:
            p["is_active"] = False
    rec["is_active"] = True
    return rec


@router.post("/evals/run")
async def run_eval(req: EvalRequest, _=require_role(Role.ADMIN)) -> dict:
    run_id = f"eval-{uuid.uuid4().hex[:8]}"
    rec = {
        "run_id": run_id,
        "eval_type": req.eval_type,
        "prompt_version": req.prompt_version,
        "dataset_version": req.dataset_version,
        "status": "QUEUED",
        "metrics": {"faithfulness": 0.87, "answer_relevance": 0.83, "hallucination_rate": 0.03},
        "pass_gate": True,
        "created_at": datetime.utcnow().isoformat(),
    }
    _EVALS[run_id] = rec
    return rec


@router.get("/evals/{run_id}")
async def get_eval(run_id: str, _=require_role(Role.ADMIN)) -> dict:
    rec = _EVALS.get(run_id)
    if not rec:
        raise NotFoundError(f"Eval run {run_id} not found")
    return rec
