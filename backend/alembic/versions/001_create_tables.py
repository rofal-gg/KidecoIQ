"""Initial schema: create all tables + PostGIS extension.

Revision ID: 001
Revises: None
Create Date: 2026-06-18
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2

# revision identifiers
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension (idempotent)
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # ── reklamasi_zones ───────────────────────────────────────
    op.create_table(
        "reklamasi_zones",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("geometry", geoalchemy2.Geometry("POLYGON", srid=4326), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("ndvi_latest", sa.Float(), nullable=True),
        sa.Column("area_ha", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ── reklamasi_history ─────────────────────────────────────
    op.create_table(
        "reklamasi_history",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("zone_id", sa.UUID(as_uuid=True), sa.ForeignKey("reklamasi_zones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ndvi_mean", sa.Float(), nullable=False),
        sa.Column("ndvi_min", sa.Float(), nullable=True),
        sa.Column("ndvi_max", sa.Float(), nullable=True),
        sa.Column("classification", sa.String(20), nullable=False),
        sa.Column("vegetation_cover_pct", sa.Float(), nullable=True),
        sa.Column("image_date", sa.Date(), nullable=False),
        sa.Column("source_band_path", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("zone_id", "image_date", name="uq_zone_image_date"),
    )

    # ── fleet_units ───────────────────────────────────────────
    op.create_table(
        "fleet_units",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("unit_id", sa.String(50), unique=True, nullable=False),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("operating_hours", sa.Float(), server_default="0"),
        sa.Column("last_latitude", sa.Float(), nullable=True),
        sa.Column("last_longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # ── fleet_logs ────────────────────────────────────────────
    op.create_table(
        "fleet_logs",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("unit_id", sa.UUID(as_uuid=True), sa.ForeignKey("fleet_units.id", ondelete="CASCADE"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("fuel_consumption", sa.Float(), nullable=True),
        sa.Column("engine_temp", sa.Float(), nullable=True),
        sa.Column("location", geoalchemy2.Geometry("POINT", srid=4326), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_fleet_logs_unit_timestamp", "fleet_logs", ["unit_id", sa.text("timestamp DESC")])

    # ── auto-update triggers for updated_at ───────────────────
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER trg_reklamasi_zones_updated_at
            BEFORE UPDATE ON reklamasi_zones
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER trg_fleet_units_updated_at
            BEFORE UPDATE ON fleet_units
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS trg_fleet_units_updated_at ON fleet_units")
    op.execute("DROP TRIGGER IF EXISTS trg_reklamasi_zones_updated_at ON reklamasi_zones")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables in reverse dependency order
    op.drop_index("idx_fleet_logs_unit_timestamp", table_name="fleet_logs")
    op.drop_table("fleet_logs")
    op.drop_table("fleet_units")
    op.drop_table("reklamasi_history")
    op.drop_table("reklamasi_zones")
