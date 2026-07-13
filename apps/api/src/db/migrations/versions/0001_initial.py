"""Initial schema — core tables, TimescaleDB hypertable, pgvector column.

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-12
"""
from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # NOTE: table DDL is generated from src.db.models via `alembic revision
    # --autogenerate`. This baseline seeds the extension + Timescale/pgvector
    # specifics that autogenerate cannot infer.

    # Convert sensor_readings into a hypertable once it exists.
    op.execute(
        "SELECT create_hypertable('sensor_readings', 'time', if_not_exists => TRUE, "
        "migrate_data => TRUE)"
    )

    # Add the DINOv2 visual embedding column (pgvector) to defects.
    op.execute("ALTER TABLE defects ADD COLUMN IF NOT EXISTS visual_embedding vector(1024)")

    # Continuous aggregate: hourly machine health summary.
    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS machine_health_hourly
        WITH (timescaledb.continuous) AS
        SELECT machine_id,
               time_bucket('1 hour', time) AS bucket,
               avg(value) AS avg_value,
               max(anomaly_score) AS max_anomaly
        FROM sensor_readings
        GROUP BY machine_id, bucket
        WITH NO DATA
        """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW IF EXISTS machine_health_hourly")
    op.execute("ALTER TABLE defects DROP COLUMN IF EXISTS visual_embedding")
