"""Create core crop planning tables"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_core_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "crop_plans",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("crop_name", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=False),
        sa.Column("soil_type", sa.String(), nullable=False),
        sa.Column("sowing_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("growth_duration_days", sa.Integer(), nullable=False),
        sa.Column("irrigation_method", sa.String(), nullable=False),
        sa.Column("land_size_acres", sa.Float(), nullable=False),
        sa.Column("expected_investment", sa.Float(), nullable=True),
        sa.Column("water_source_type", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "crop_stages",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("crop_plan_id", sa.String(), sa.ForeignKey("crop_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", sa.String(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("recommended_irrigation_frequency_days", sa.Integer(), nullable=False),
    )

    op.create_table(
        "irrigation_schedule",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("crop_plan_id", sa.String(), sa.ForeignKey("crop_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stage", sa.String(), nullable=False),
        sa.Column("water_amount_liters", sa.Integer(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("auto_adjusted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "irrigation_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("crop_plan_id", sa.String(), sa.ForeignKey("crop_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("original_amount", sa.Integer(), nullable=False),
        sa.Column("adjusted_amount", sa.Integer(), nullable=False),
        sa.Column("weather_adjustment", sa.Text(), nullable=True),
        sa.Column("auto_triggered", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "weather_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("crop_plan_id", sa.String(), sa.ForeignKey("crop_plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("weather_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("temp", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Float(), nullable=True),
        sa.Column("rain", sa.Float(), nullable=True),
        sa.Column("rain_chance", sa.Float(), nullable=True),
        sa.Column("raw_payload", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_index("ix_crop_plans_user_id", "crop_plans", ["user_id"])
    op.create_index("ix_crop_plans_crop_name", "crop_plans", ["crop_name"])
    op.create_index("ix_crop_stages_crop_plan_id", "crop_stages", ["crop_plan_id"])
    op.create_index("ix_irrigation_schedule_crop_plan_id", "irrigation_schedule", ["crop_plan_id"])
    op.create_index("ix_irrigation_schedule_date", "irrigation_schedule", ["date"])
    op.create_index("ix_irrigation_logs_crop_plan_id", "irrigation_logs", ["crop_plan_id"])
    op.create_index("ix_weather_logs_crop_plan_id", "weather_logs", ["crop_plan_id"])


def downgrade():
    op.drop_index("ix_weather_logs_crop_plan_id", table_name="weather_logs")
    op.drop_index("ix_irrigation_logs_crop_plan_id", table_name="irrigation_logs")
    op.drop_index("ix_irrigation_schedule_date", table_name="irrigation_schedule")
    op.drop_index("ix_irrigation_schedule_crop_plan_id", table_name="irrigation_schedule")
    op.drop_index("ix_crop_stages_crop_plan_id", table_name="crop_stages")
    op.drop_index("ix_crop_plans_crop_name", table_name="crop_plans")
    op.drop_index("ix_crop_plans_user_id", table_name="crop_plans")
    op.drop_table("weather_logs")
    op.drop_table("irrigation_logs")
    op.drop_table("irrigation_schedule")
    op.drop_table("crop_stages")
    op.drop_table("crop_plans")
