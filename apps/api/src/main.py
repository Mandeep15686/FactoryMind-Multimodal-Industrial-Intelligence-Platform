"""FastAPI application entrypoint for the FactoryMind API service."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.exceptions import register_exception_handlers
from src.core.observability import configure_logging, configure_tracing

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201
    # Startup: warm shared clients (mock-safe). Real connections open lazily.
    yield
    # Shutdown: nothing to close in mock mode.


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.app_name} API",
        version="1.0.0",
        description="Multimodal Industrial Intelligence Platform",
        docs_url="/docs",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.environment == "dev" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    configure_tracing(app)

    # Mount routers (created in src/routers). Imported lazily to keep the
    # module importable even while sub-packages are being generated.
    from src.routers import api_router, webhook_router, ws_router

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(ws_router)
    app.include_router(webhook_router)

    @app.get("/health", tags=["system"])
    async def health() -> dict:
        return {"status": "ok", "service": settings.app_name, "env": settings.environment}

    if settings.prometheus_enabled:
        try:  # pragma: no cover
            from prometheus_client import make_asgi_app

            app.mount("/metrics", make_asgi_app())
        except Exception:
            pass

    return app


app = create_app()
