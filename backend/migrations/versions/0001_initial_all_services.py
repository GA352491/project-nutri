"""Initial schema — all 5 PostgreSQL services

Revision ID: 0001
Revises: None
Create Date: 2026-08-19

Creates tables for:
  nutriplan_auth      → users
  nutriplan_diary     → diary_entries, daily_summaries
  nutriplan_grocery   → grocery_lists, grocery_items
  nutriplan_meal_plan → meal_plans, meal_plan_items
  nutriplan_subs      → subscriptions
"""
from typing import Sequence, Union
import uuid
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── AUTH: users ──────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id",              postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("email",           sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name",       sa.String(255), nullable=False),
        sa.Column("role",            sa.String(50),  nullable=False, server_default="member"),
        sa.Column("is_active",       sa.Boolean(),   nullable=False, server_default=sa.true()),
        sa.Column("is_verified",     sa.Boolean(),   nullable=False, server_default=sa.false()),
        sa.Column("created_at",      sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at",      sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── DIARY: diary_entries ──────────────────────────────────────────────────
    op.create_table(
        "diary_entries",
        sa.Column("id",          postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id",     postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("log_date",    sa.Date(),       nullable=False),
        sa.Column("meal_type",   sa.String(20),   nullable=False),
        sa.Column("source",      sa.String(20),   nullable=False, server_default="manual"),
        sa.Column("recipe_id",   sa.String(255),  nullable=True),
        sa.Column("food_name",   sa.String(255),  nullable=False),
        sa.Column("quantity_g",  sa.Float(),      nullable=False, server_default="100"),
        sa.Column("calories",    sa.Float(),      nullable=False, server_default="0"),
        sa.Column("protein_g",   sa.Float(),      nullable=False, server_default="0"),
        sa.Column("fat_g",       sa.Float(),      nullable=False, server_default="0"),
        sa.Column("carbs_g",     sa.Float(),      nullable=False, server_default="0"),
        sa.Column("fiber_g",     sa.Float(),      nullable=False, server_default="0"),
        sa.Column("photo_path",  sa.String(512),  nullable=True),
        sa.Column("notes",       sa.Text(),       nullable=True),
    )
    op.create_index("ix_diary_entries_user_id",  "diary_entries", ["user_id"])
    op.create_index("ix_diary_entries_log_date", "diary_entries", ["log_date"])

    # ── DIARY: daily_summaries ────────────────────────────────────────────────
    op.create_table(
        "daily_summaries",
        sa.Column("id",             postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id",        postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("log_date",       sa.Date(),  nullable=False),
        sa.Column("total_calories", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_protein_g",sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_fat_g",    sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_carbs_g",  sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_fiber_g",  sa.Float(), nullable=False, server_default="0"),
        sa.Column("entry_count",    sa.Integer(),nullable=False, server_default="0"),
    )
    op.create_index("ix_daily_summaries_user_id",  "daily_summaries", ["user_id"])
    op.create_index("ix_daily_summaries_log_date", "daily_summaries", ["log_date"])

    # ── GROCERY: grocery_lists ────────────────────────────────────────────────
    op.create_table(
        "grocery_lists",
        sa.Column("id",      postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name",    sa.String(255), nullable=False, server_default="Weekly List"),
    )
    op.create_index("ix_grocery_lists_user_id", "grocery_lists", ["user_id"])

    # ── GROCERY: grocery_items ────────────────────────────────────────────────
    op.create_table(
        "grocery_items",
        sa.Column("id",               postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("list_id",          postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name",             sa.String(255), nullable=False),
        sa.Column("quantity",         sa.String(100), nullable=False, server_default="1"),
        sa.Column("unit",             sa.String(50),  nullable=False, server_default=""),
        sa.Column("category",         sa.String(100), nullable=False, server_default="General"),
        sa.Column("is_checked",       sa.Boolean(),   nullable=False, server_default=sa.false()),
        sa.Column("source_recipe_id", sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(["list_id"], ["grocery_lists.id"], ondelete="CASCADE"),
    )

    # ── MEAL PLAN: meal_plans ─────────────────────────────────────────────────
    op.create_table(
        "meal_plans",
        sa.Column("id",         postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id",    postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(),       nullable=False),
        sa.Column("end_date",   sa.Date(),       nullable=False),
        sa.Column("status",     sa.String(20),   nullable=False, server_default="active"),
        sa.Column("targets",    postgresql.JSON, nullable=True),
    )
    op.create_index("ix_meal_plans_user_id", "meal_plans", ["user_id"])

    # ── MEAL PLAN: meal_plan_items ────────────────────────────────────────────
    op.create_table(
        "meal_plan_items",
        sa.Column("id",        postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("plan_id",   postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date",      sa.Date(),       nullable=False),
        sa.Column("meal_type", sa.String(20),   nullable=False),
        sa.Column("recipe_id", sa.String(255),  nullable=True),
        sa.Column("calories",  sa.Float(),      nullable=False, server_default="0"),
        sa.Column("protein_g", sa.Float(),      nullable=False, server_default="0"),
        sa.Column("fat_g",     sa.Float(),      nullable=False, server_default="0"),
        sa.Column("carbs_g",   sa.Float(),      nullable=False, server_default="0"),
        sa.Column("status",    sa.String(20),   nullable=False, server_default="planned"),
        sa.ForeignKeyConstraint(["plan_id"], ["meal_plans.id"], ondelete="CASCADE"),
    )

    # ── SUBSCRIPTIONS: subscriptions ──────────────────────────────────────────
    op.create_table(
        "subscriptions",
        sa.Column("id",                       postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id",                  postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tier",                     sa.String(50), nullable=False, server_default="free"),
        sa.Column("status",                   sa.String(50), nullable=False, server_default="active"),
        sa.Column("current_period_start",     sa.DateTime(), nullable=False),
        sa.Column("current_period_end",       sa.DateTime(), nullable=False),
        sa.Column("provider",                 sa.String(50), nullable=False, server_default="mock"),
        sa.Column("provider_subscription_id", sa.String(100), nullable=True),
        sa.Column("cancel_at_period_end",     sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"], unique=True)


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("subscriptions")
    op.drop_table("meal_plan_items")
    op.drop_table("meal_plans")
    op.drop_table("grocery_items")
    op.drop_table("grocery_lists")
    op.drop_table("daily_summaries")
    op.drop_table("diary_entries")
    op.drop_table("users")
