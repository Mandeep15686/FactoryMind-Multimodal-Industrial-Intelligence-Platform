.DEFAULT_GOAL := help
API := apps/api
COMPOSE := docker compose -f docker-compose.dev.yaml

.PHONY: help dev down logs install test lint typecheck eval fmt migrate seed smoke

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

dev: ## Boot the full local stack (<60s)
	$(COMPOSE) up -d --build
	@echo "API   → http://localhost:8000/docs"
	@echo "Web   → http://localhost:3000"
	@echo "Langfuse → http://localhost:3001"

down: ## Stop the local stack
	$(COMPOSE) down

logs: ## Tail all service logs
	$(COMPOSE) logs -f

install: ## Install API + web deps
	cd $(API) && pip install ".[dev]"
	cd apps/web && npm install

test: ## Run API unit + eval tests
	cd $(API) && HF_USE_MOCK=true pytest -q tests/unit tests/eval

smoke: ## Run the end-to-end agent smoke test
	cd $(API) && HF_USE_MOCK=true pytest -q tests/unit/test_smoke.py

lint: ## Ruff lint
	cd $(API) && ruff check src

typecheck: ## mypy (api) + tsc (web)
	cd $(API) && mypy src || true
	cd apps/web && npm run typecheck

fmt: ## Auto-format with ruff
	cd $(API) && ruff check --fix src && ruff format src

eval: ## Run the offline evaluation gate
	cd $(API) && HF_USE_MOCK=true python ../../evals/offline_eval_runner.py

migrate: ## Apply Alembic migrations
	cd $(API) && alembic upgrade head

seed: ## Seed the knowledge base (in-memory corpus is auto-seeded)
	@echo "Knowledge corpus auto-seeds from src/rag/_corpus.py on first query"
