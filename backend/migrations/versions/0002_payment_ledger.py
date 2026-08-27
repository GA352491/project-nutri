"""Payment ledger tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-21

Creates tables for:
  nutriplan_payments → payments, connect_accounts, webhook_events
"""
from typing import Sequence, Union
import uuid
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", sa.String(100), nullable=True),
        sa.Column("purpose", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("amount_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="usd"),
        sa.Column("platform_fee_cents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provider", sa.String(50), nullable=False, server_default="stripe"),
        sa.Column("provider_object_id", sa.String(100), nullable=True),
        sa.Column("destination_account_id", sa.String(100), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("reference_id", sa.String(100), nullable=True),
        sa.Column("extra_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_payments_user_id", "payments", ["user_id"])
    op.create_index("ix_payments_purpose", "payments", ["purpose"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_provider_object_id", "payments", ["provider_object_id"], unique=True)
    op.create_index("ix_payments_reference_type", "payments", ["reference_type"])
    op.create_index("ix_payments_reference_id", "payments", ["reference_id"])

    op.create_table(
        "connect_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("nutritionist_id", sa.String(100), nullable=False),
        sa.Column("stripe_account_id", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("charges_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_connect_accounts_nutritionist_id", "connect_accounts", ["nutritionist_id"], unique=True)
    op.create_index("ix_connect_accounts_stripe_account_id", "connect_accounts", ["stripe_account_id"], unique=True)

    op.create_table(
        "webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("stripe_event_id", sa.String(100), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("received_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_webhook_events_stripe_event_id", "webhook_events", ["stripe_event_id"], unique=True)
    op.create_index("ix_webhook_events_event_type", "webhook_events", ["event_type"])


def downgrade() -> None:
    op.drop_table("webhook_events")
    op.drop_table("connect_accounts")
    op.drop_table("payments")
