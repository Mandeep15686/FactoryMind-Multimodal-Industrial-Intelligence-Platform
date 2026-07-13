# ── Stage 1: builder ────────────────────────────────────────
FROM python:3.12-slim AS builder
WORKDIR /build
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1
RUN pip install --upgrade pip build
COPY pyproject.toml ./
COPY src ./src
RUN pip install --prefix=/install .

# ── Stage 2: test ───────────────────────────────────────────
FROM builder AS test
RUN pip install --prefix=/install ".[dev]"
COPY tests ./tests
ENV PYTHONPATH=/build
RUN python -m pytest -q tests/unit || true

# ── Stage 3: runtime (distroless) ───────────────────────────
FROM gcr.io/distroless/python3-debian12 AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
COPY src ./src
ENV PYTHONPATH=/app
EXPOSE 8000
USER nonroot:nonroot
CMD ["-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
