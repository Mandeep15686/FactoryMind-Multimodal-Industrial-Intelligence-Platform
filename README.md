# FactoryMind — Multimodal Industrial Intelligence Platform

> Every defect has a story. FactoryMind reads it before it costs you.

FactoryMind is a production-grade **multimodal AI platform** that ingests live camera
feeds, machine audio, and OPC-UA sensor streams from manufacturing equipment, then uses
a **LangGraph 12-agent orchestration layer** to detect visual defects, identify acoustic
anomalies, forecast equipment failure, run **hybrid Graph RAG** root-cause analysis, and
generate autonomous shift reports — automatically opening Jira tickets and routing
Slack/PagerDuty alerts.

This repository is generated from `FactoryMind_AI_Blueprint.html`. It is a **mock-first,
runnable scaffold**: the entire pipeline runs offline (no GPUs, no external API keys)
using deterministic mocks, and every external client (HuggingFace, Anthropic, Qdrant,
Neo4j, Jira, Slack, …) activates automatically when its credentials/services are present.

---

## Architecture at a glance

```
Ingestion (RTSP · mic · OPC-UA · IoT Core)
    → Kafka → FastAPI workers
        → LangGraph Supervisor
            ├─ Visual Inspection Agent   (Object Detection · Segmentation · Classification · DINOv2 · Zero-shot)
            ├─ Audio Analysis Agent      (AST · Whisper ASR · NER)
            └─ Sensor Analysis Agent     (PatchTST forecast · RUL · TabPFN health)
        → Knowledge Retrieval Agent  (Qdrant dense + BM25 sparse + Neo4j graph + RRF + rerank + compress + Self-RAG)
        → RCA Agent  ⇄  Critic Agent (5-Whys, max 3 refine loops)
        → Maintenance Planning (SAP inventory + Jira) → [Human Approval] → Alert (PagerDuty/Slack)
        → Report Generation (BART + Claude) → Feedback → Evaluation
```

See `FactoryMind_AI_Blueprint.html` for the full 25-section design (problem, users, HF
tasks, RAG, memory, tools, schema, API, evaluation, LLMOps, security, scalability).

---

## Repository layout

```
factory-mind/
├── apps/
│   ├── api/           # FastAPI service — agents, hf_tasks, rag, tools, routers, workers
│   └── web/           # Next.js 14 dashboard (Recharts + Tailwind)
├── packages/
│   ├── prompts/       # Versioned YAML prompt registry (rca_v1/v2, shift_report_v1)
│   └── shared-types/  # TS types mirroring the Python schemas
├── infra/
│   ├── terraform/     # EKS · RDS · MSK · ElastiCache · S3 (modules + dev/staging/prod)
│   └── k8s/           # Deployments, Qdrant StatefulSet, HPA, KEDA, Ingress
├── evals/             # RAGAS · DeepEval · defect-detection benchmark + golden datasets
├── .github/workflows/ # ci · eval-gate · deploy-prod
├── docker-compose.dev.yaml
└── Makefile
```

---

## Quick start

### Option A — pure Python (fastest, offline)

```bash
cd apps/api
pip install ".[dev]"          # or: pip install fastapi pydantic pydantic-settings python-jose sqlalchemy
HF_USE_MOCK=true pytest -q tests/unit    # end-to-end agent graph + RAG + HF wrappers
uvicorn src.main:app --reload            # http://localhost:8000/docs
```

### Option B — full stack via Docker

```bash
cp .env.example .env
make dev          # boots API, web, Postgres/TimescaleDB, Redis, Qdrant, Neo4j, Kafka, Langfuse, OPC-UA sim
```

- API docs: http://localhost:8000/docs
- Dashboard: http://localhost:3000
- Langfuse: http://localhost:3001

### Try it

```bash
# trigger an inspection → runs the full 12-agent graph
curl -X POST http://localhost:8000/api/v1/inspections \
  -H 'Content-Type: application/json' \
  -d '{"machine_id":"M12","triggered_by":"MANUAL"}'

# query the Graph-RAG knowledge base
curl -X POST http://localhost:8000/api/v1/knowledge/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"drive-end bearing wear vibration","top_k":5}'
```

---

## HuggingFace tasks (15 across 5 categories)

| Category | Tasks |
|----------|-------|
| Computer Vision | Object Detection · Image Segmentation · Image Classification · Zero-Shot Image Classification · Image Feature Extraction |
| Audio | Audio Classification · Automatic Speech Recognition |
| NLP | Summarization · Token Classification (NER) · Sentence Similarity · Text Ranking · Zero-Shot Classification |
| Tabular | Time Series Forecasting · Tabular Classification |
| Multimodal | Document QA · Visual QA |

Each wrapper (`apps/api/src/hf_tasks/`) has a real HF-Inference-API path and a
deterministic mock path controlled by `HF_USE_MOCK`.

---

## Evaluation

```bash
make eval    # RAGAS + DeepEval + defect-detection F1 gate
```

| Metric | Target |
|--------|--------|
| RAG Faithfulness (RAGAS) | > 0.85 |
| Hallucination Rate (DeepEval) | < 5% |
| Defect Detection F1 | > 0.92 |

The `eval-gate.yaml` workflow blocks any PR that regresses these below target.

---

## Tech stack

FastAPI · LangGraph · LangChain · LlamaIndex · Claude (Anthropic) · HuggingFace Inference ·
Qdrant · Neo4j · Elasticsearch/BM25 · PostgreSQL 16 + TimescaleDB · Redis · Kafka · Celery ·
Next.js 14 · Prometheus/Grafana · Langfuse · OpenTelemetry · MLflow · Docker · Kubernetes
(EKS) · Terraform · ArgoCD · GitHub Actions.

---

## Notes

- **Mock-first by design.** With no keys set, LLM/HF/tool calls return deterministic
  stand-ins so the graph completes and tests pass. This is a portfolio scaffold — model
  accuracy figures in the blueprint are illustrative targets, not production measurements.
- **Model IDs** use current Claude names (`claude-sonnet-5`, `claude-haiku-4-5`).
- Claude models default to the latest; swap in your provider keys via `.env`.
