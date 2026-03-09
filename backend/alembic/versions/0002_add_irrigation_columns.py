"""Add missing irrigation schedule columns

Revision ID: 0002_add_irrigation_columns
Revises: 0001_create_core_tables
Create Date: 2026-02-21
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_add_irrigation_columns"
down_revision = "0001_create_core_tables"
branch_labels = None
depends_on = None


def upgrade():
    # Add columns that were added to models but missing in initial migration
    op.add_column(
        "irrigation_schedule",
        sa.Column("actual_liters", sa.Integer(), nullable=True, server_default=sa.text("0")),
    )
    op.add_column(
        "irrigation_schedule",
        sa.Column("weather_adjustment_percent", sa.Float(), nullable=True, server_default=sa.text("0")),
    )
    op.add_column(
        "irrigation_schedule",
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_column("irrigation_schedule", "executed_at")
    op.drop_column("irrigation_schedule", "weather_adjustment_percent")
    op.drop_column("irrigation_schedule", "actual_liters")
