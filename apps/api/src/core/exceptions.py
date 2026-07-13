"""Domain exceptions + FastAPI exception handlers."""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class FactoryMindError(Exception):
    """Base for all domain errors."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "internal_error"

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(FactoryMindError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ValidationError(FactoryMindError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    code = "validation_error"


class AuthError(FactoryMindError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"


class ForbiddenError(FactoryMindError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "forbidden"


class ToolExecutionError(FactoryMindError):
    status_code = status.HTTP_502_BAD_GATEWAY
    code = "tool_execution_error"


class AgentExecutionError(FactoryMindError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "agent_execution_error"


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(FactoryMindError)
    async def _handle(request: Request, exc: FactoryMindError):  # noqa: ANN202
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
        )
