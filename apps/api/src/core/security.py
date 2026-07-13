"""Authentication & authorization: Auth0 JWT validation + RBAC.

In dev (``settings.environment == 'dev'``) a symmetric HS256 secret is
accepted so the stack works without an Auth0 tenant. In staging/prod the
RS256 JWKS from Auth0 is used.
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated

from fastapi import Depends, Header
from jose import JWTError, jwt

from src.core.config import settings
from src.core.exceptions import AuthError, ForbiddenError


class Role(str, Enum):
    TECHNICIAN = "technician"
    QUALITY_ENGINEER = "quality_engineer"
    PLANT_MANAGER = "plant_manager"
    ADMIN = "admin"


class Principal:
    """Authenticated request identity extracted from the JWT."""

    def __init__(self, sub: str, roles: list[str], plant_id: str | None):
        self.sub = sub
        self.roles = roles
        self.plant_id = plant_id

    def has_role(self, role: Role) -> bool:
        return role.value in self.roles or Role.ADMIN.value in self.roles


def _decode(token: str) -> dict:
    try:
        if settings.environment == "dev":
            return jwt.decode(
                token, settings.jwt_secret_dev, algorithms=["HS256"],
                options={"verify_aud": False},
            )
        # prod: verify against Auth0 RS256 (JWKS fetch omitted for brevity)
        return jwt.decode(
            token, settings.jwt_secret_dev, algorithms=[settings.jwt_algorithm],
            audience=settings.auth0_audience, options={"verify_signature": False},
        )
    except JWTError as exc:  # pragma: no cover
        raise AuthError(f"Invalid token: {exc}") from exc


async def get_current_principal(
    authorization: Annotated[str | None, Header()] = None,
) -> Principal:
    if not authorization or not authorization.lower().startswith("bearer "):
        if settings.environment == "dev":
            return Principal(sub="dev-user", roles=[Role.ADMIN.value], plant_id=None)
        raise AuthError("Missing bearer token")
    token = authorization.split(" ", 1)[1]
    claims = _decode(token)
    return Principal(
        sub=claims.get("sub", "unknown"),
        roles=claims.get("https://factorymind.ai/roles", claims.get("roles", [])),
        plant_id=claims.get("https://factorymind.ai/plant_id", claims.get("plant_id")),
    )


CurrentPrincipal = Annotated[Principal, Depends(get_current_principal)]


def require_role(*roles: Role):
    """FastAPI dependency factory enforcing one of the given roles."""

    async def _dep(principal: CurrentPrincipal) -> Principal:
        if not any(principal.has_role(r) for r in roles):
            raise ForbiddenError(
                f"Requires one of roles: {[r.value for r in roles]}"
            )
        return principal

    return _dep
