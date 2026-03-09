"""Align column types to match SQLAlchemy models

Revision ID: 0003_align_column_types
Revises: 0002_add_irrigation_columns
Create Date: 2026-02-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_align_column_types"
down_revision = "0002_add_irrigation_columns"
branch_labels = None
depends_on = None


def upgrade():
    # Drop FK constraints referencing crop_plans to allow type changes
    op.execute("ALTER TABLE crop_stages DROP CONSTRAINT IF EXISTS crop_stages_crop_plan_id_fkey")
    op.execute("ALTER TABLE irrigation_schedule DROP CONSTRAINT IF EXISTS irrigation_schedule_crop_plan_id_fkey")
    op.execute("ALTER TABLE irrigation_logs DROP CONSTRAINT IF EXISTS irrigation_logs_crop_plan_id_fkey")
    op.execute("ALTER TABLE weather_logs DROP CONSTRAINT IF EXISTS weather_logs_crop_plan_id_fkey")

    # Convert id and foreign key columns from string to native UUID where appropriate
    op.execute("ALTER TABLE crop_plans ALTER COLUMN id TYPE UUID USING id::uuid")
    op.execute("ALTER TABLE crop_stages ALTER COLUMN id TYPE UUID USING id::uuid")
    op.execute("ALTER TABLE crop_stages ALTER COLUMN crop_plan_id TYPE UUID USING crop_plan_id::uuid")
    op.execute("ALTER TABLE irrigation_schedule ALTER COLUMN id TYPE UUID USING id::uuid")
    op.execute("ALTER TABLE irrigation_schedule ALTER COLUMN crop_plan_id TYPE UUID USING crop_plan_id::uuid")
    op.execute("ALTER TABLE weather_logs ALTER COLUMN id TYPE UUID USING id::uuid")
    op.execute("ALTER TABLE weather_logs ALTER COLUMN crop_plan_id TYPE UUID USING crop_plan_id::uuid")

    # Recreate irrigation_logs to match model (integer autoincrement PK)
    op.drop_table("irrigation_logs")
    op.create_table(
        "irrigation_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column("crop_plan_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crop_plans.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("irrigation_date", sa.Date(), nullable=False),
        sa.Column("original_amount", sa.Float(), nullable=False),
        sa.Column("adjusted_amount", sa.Float(), nullable=False),
        sa.Column("weather_adjustment", sa.Text(), nullable=True),
        sa.Column("weather_adjustment_percent", sa.Float(), nullable=True, server_default=sa.text("0")),
        sa.Column("planned_liters", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("actual_liters", sa.Float(), nullable=False, server_default=sa.text("0")),
        sa.Column("duration_seconds", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'completed'")),
        sa.Column("auto_triggered", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Recreate FK constraints
    op.execute("ALTER TABLE crop_stages ADD CONSTRAINT crop_stages_crop_plan_id_fkey FOREIGN KEY (crop_plan_id) REFERENCES crop_plans(id) ON DELETE CASCADE")
    op.execute("ALTER TABLE irrigation_schedule ADD CONSTRAINT irrigation_schedule_crop_plan_id_fkey FOREIGN KEY (crop_plan_id) REFERENCES crop_plans(id) ON DELETE CASCADE")
    op.execute("ALTER TABLE weather_logs ADD CONSTRAINT weather_logs_crop_plan_id_fkey FOREIGN KEY (crop_plan_id) REFERENCES crop_plans(id) ON DELETE SET NULL")


def downgrade():
    # Downgrade: not implemented because destructive changes were applied.
    raise NotImplementedError("Downgrade not supported for 0003_align_column_types")
