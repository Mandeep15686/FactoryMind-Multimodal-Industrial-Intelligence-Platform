"""Application configuration via Pydantic Settings.

All runtime configuration is loaded from environment variables (12-factor).
In production these are injected from AWS Secrets Manager via the
Kubernetes ExternalSecrets Operator — never committed to source.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object. Import via ``get_settings()``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────
    app_name: str = "FactoryMind"
    environment: Literal["dev", "staging", "prod"] = "dev"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    # ── Server ───────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # ── Postgres / TimescaleDB ───────────────────────────
    database_url: str = "postgresql+asyncpg://factory:factory@localhost:5432/factorymind"
    db_pool_size: int = 20
    db_max_overflow: int = 10

    # ── Redis ────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_session_ttl_s: int = 4 * 3600
    semantic_cache_ttl_s: int = 30 * 60
    semantic_cache_threshold: float = 0.95

    # ── Kafka ────────────────────────────────────────────
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_events_topic: str = "factorymind.events"
    kafka_consumer_group: str = "factorymind-workers"

    # ── Vector / Graph / Sparse stores ───────────────────
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "factorymind_knowledge"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    elasticsearch_url: str = "http://localhost:9200"
    bm25_index: str = "factorymind_bm25"

    # ── Object storage ───────────────────────────────────
    s3_bucket: str = "factorymind-artifacts"
    aws_region: str = "us-east-1"

    # ── LLM providers ────────────────────────────────────
    anthropic_api_key: str = Field(default="", repr=False)
    openai_api_key: str = Field(default="", repr=False)
    primary_llm_model: str = "claude-sonnet-5"
    fallback_llm_model: str = "gpt-4o"
    judge_llm_model: str = "claude-haiku-4-5-20251001"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096

    # ── HuggingFace inference ────────────────────────────
    hf_api_token: str = Field(default="", repr=False)
    hf_inference_endpoint: str = "https://api-inference.huggingface.co/models"
    hf_use_mock: bool = True  # dev default — no external calls

    # ── Embeddings ───────────────────────────────────────
    text_embedding_model: str = "BAAI/bge-m3"
    text_embedding_dim: int = 1024
    visual_embedding_model: str = "facebook/dinov2-large"
    visual_embedding_dim: int = 1024
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"

    # ── RAG tuning ───────────────────────────────────────
    retrieval_top_k: int = 20
    rerank_top_k: int = 5
    rrf_k: int = 60
    dense_weight: float = 0.7
    sparse_weight: float = 0.3
    self_rag_threshold: float = 0.70
    multi_query_variants: int = 3

    # ── Agent / RCA control ──────────────────────────────
    max_rca_iterations: int = 3
    critic_confidence_threshold: float = 0.75
    approval_timeout_s: int = 15 * 60
    high_cost_approval_usd: float = 10_000.0

    # ── Auth ─────────────────────────────────────────────
    auth0_domain: str = "factorymind.us.auth0.com"
    auth0_audience: str = "https://api.factorymind.ai"
    jwt_algorithm: str = "RS256"
    jwt_secret_dev: str = Field(default="dev-insecure-secret-change-me", repr=False)

    # ── Observability ────────────────────────────────────
    langfuse_public_key: str = Field(default="", repr=False)
    langfuse_secret_key: str = Field(default="", repr=False)
    langfuse_host: str = "http://localhost:3001"
    otel_exporter_endpoint: str = "http://localhost:4317"
    prometheus_enabled: bool = True

    # ── External integrations ────────────────────────────
    jira_base_url: str = "https://factorymind.atlassian.net"
    jira_email: str = Field(default="", repr=False)
    jira_api_token: str = Field(default="", repr=False)
    jira_project_key: str = "MAINT"
    slack_bot_token: str = Field(default="", repr=False)
    slack_signing_secret: str = Field(default="", repr=False)
    pagerduty_routing_key: str = Field(default="", repr=False)
    sap_base_url: str = "https://sap.factorymind.internal"
    sap_api_key: str = Field(default="", repr=False)
    sendgrid_api_key: str = Field(default="", repr=False)
    grafana_url: str = "http://localhost:3000"
    grafana_api_key: str = Field(default="", repr=False)

    @property
    def is_prod(self) -> bool:
        return self.environment == "prod"


@lru_cache
def get_settings() -> Settings:
    """Cached singleton accessor for settings."""
    return Settings()


settings = get_settings()
