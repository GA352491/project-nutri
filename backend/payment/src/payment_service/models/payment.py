"""
Payment-service owned models.

Money movement lives here — not on Appointment, Subscription, Grocery, or
Marketplace documents. Those services keep a reference id (appointment_id,
order_id, user_id) and query this service for status, amounts, and provider ids.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Payment(Base):
    """
    Ledger row for every Stripe PaymentIntent or SetupIntent created by this service.

    One row per provider object. Status is updated from Stripe webhooks so
    booking/grocery/subscription services do not need to store PI payloads.
    """

    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Callers use mixed ids (UUID users and string mocks like usr_patient_01)
    user_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)

    # booking | grocery_hold | subscription_charge | setup_intent
    purpose: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    # pending | requires_action | succeeded | failed | canceled | refunded
    status: Mapped[str] = mapped_column(String(50), index=True, default="pending")

    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="usd")
    platform_fee_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    provider: Mapped[str] = mapped_column(String(50), nullable=False, default="stripe")
    provider_object_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    destination_account_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # appointment | grocery_order | subscription | connect
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)

    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ConnectAccount(Base):
    """
    Stripe Connect Express account for a nutritionist.

    Marketplace may cache stripe_account_id for display; this table is the
    payment-owned mapping used for destination charges and webhook updates.
    """

    __tablename__ = "connect_accounts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nutritionist_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    stripe_account_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    charges_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebhookEvent(Base):
    """Idempotency log so Stripe retries do not double-apply status changes."""

    __tablename__ = "webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stripe_event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
