"""
Persistence for payment-owned records.

Stripe API calls stay in stripe_provider; this module is the local ledger.
Writes are best-effort so local Stripe checkout still works if Postgres is down.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import settings
from ..models.payment import Base, ConnectAccount, Payment, WebhookEvent

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        pass


def _purpose_from_metadata(metadata: Optional[dict], default: str = "booking") -> tuple[str, str]:
    meta = metadata or {}
    kind = meta.get("type")
    if kind == "grocery_hold":
        return "grocery_hold", "grocery_order"
    if kind == "subscription_charge":
        return "subscription_charge", "subscription"
    if default == "setup_intent":
        return "setup_intent", "subscription"
    return "booking", "appointment"


def _reference_id(metadata: Optional[dict], fallback: Optional[str]) -> Optional[str]:
    meta = metadata or {}
    return meta.get("order_id") or meta.get("appointment_id") or fallback


def _user_id(metadata: Optional[dict], explicit: Optional[str] = None) -> Optional[str]:
    if explicit:
        return explicit
    meta = metadata or {}
    return meta.get("user_id")


async def record_payment_intent(
    *,
    amount_cents: int,
    currency: str,
    platform_fee_cents: int,
    provider_object_id: str,
    destination_account_id: Optional[str],
    reference_id: str,
    metadata: Optional[dict] = None,
    user_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> Optional[Payment]:
    purpose, reference_type = _purpose_from_metadata(metadata)
    payment = Payment(
        user_id=_user_id(metadata, user_id),
        purpose=purpose,
        status="pending",
        amount_cents=amount_cents,
        currency=currency or "usd",
        platform_fee_cents=platform_fee_cents or 0,
        provider="stripe",
        provider_object_id=provider_object_id,
        destination_account_id=destination_account_id,
        reference_type=reference_type,
        reference_id=_reference_id(metadata, reference_id),
        extra_metadata=metadata,
    )
    return await _save(payment, db)


async def record_setup_intent(
    *,
    provider_object_id: str,
    metadata: Optional[dict] = None,
    user_id: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> Optional[Payment]:
    payment = Payment(
        user_id=_user_id(metadata, user_id),
        purpose="setup_intent",
        status="requires_action",
        amount_cents=0,
        currency="usd",
        platform_fee_cents=0,
        provider="stripe",
        provider_object_id=provider_object_id,
        reference_type="subscription",
        reference_id=_user_id(metadata, user_id),
        extra_metadata=metadata,
    )
    return await _save(payment, db)


async def record_connect_account(
    *,
    nutritionist_id: str,
    stripe_account_id: str,
    email: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> Optional[ConnectAccount]:
    account = ConnectAccount(
        nutritionist_id=nutritionist_id,
        stripe_account_id=stripe_account_id,
        email=email or None,
        charges_enabled=False,
    )
    return await _save(account, db)


async def get_payment(payment_id: uuid.UUID, db: Optional[AsyncSession] = None) -> Optional[Payment]:
    session = db
    close = False
    try:
        if session is None:
            session = AsyncSessionLocal()
            close = True
        result = await session.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalars().first()
    except Exception as e:
        print(f"[PaymentStore] get_payment skipped: {e}")
        return None
    finally:
        if close and session:
            await session.close()


async def get_payment_by_provider_id(provider_object_id: str, db: Optional[AsyncSession] = None) -> Optional[Payment]:
    session = db
    close = False
    try:
        if session is None:
            session = AsyncSessionLocal()
            close = True
        result = await session.execute(
            select(Payment).where(Payment.provider_object_id == provider_object_id)
        )
        return result.scalars().first()
    except Exception as e:
        print(f"[PaymentStore] get_payment_by_provider_id skipped: {e}")
        return None
    finally:
        if close and session:
            await session.close()


async def list_payments_by_reference(reference_id: str, db: Optional[AsyncSession] = None) -> list[Payment]:
    session = db
    close = False
    try:
        if session is None:
            session = AsyncSessionLocal()
            close = True
        result = await session.execute(
            select(Payment).where(Payment.reference_id == reference_id).order_by(Payment.created_at.desc())
        )
        return list(result.scalars().all())
    except Exception as e:
        print(f"[PaymentStore] list_payments_by_reference skipped: {e}")
        return []
    finally:
        if close and session:
            await session.close()


def _mapping(obj) -> dict:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict"):
        try:
            return obj.to_dict()
        except Exception:
            pass
    try:
        return dict(obj)
    except Exception:
        return {}


async def apply_webhook_event(event, db: Optional[AsyncSession] = None) -> dict:
    """
    Persist webhook idempotently and update Payment / ConnectAccount rows.
    Returns a small summary for the HTTP response.
    """
    event_map = _mapping(event)
    event_id = event_map.get("id") or ""
    event_type = event_map.get("type") or ""
    obj = _mapping(_mapping(event_map.get("data")).get("object"))

    session = db
    close = False
    try:
        if session is None:
            session = AsyncSessionLocal()
            close = True

        if event_id:
            existing = await session.execute(
                select(WebhookEvent).where(WebhookEvent.stripe_event_id == event_id)
            )
            if existing.scalars().first():
                return {"status": "duplicate", "event_type": event_type}

            row = WebhookEvent(
                stripe_event_id=event_id,
                event_type=event_type,
                processed=False,
                payload={"id": event_id, "type": event_type, "object_id": obj.get("id")},
            )
            session.add(row)
            await session.flush()

        summary = {"status": "ok", "event_type": event_type}

        if event_type in ("payment_intent.succeeded", "payment_intent.payment_failed", "payment_intent.canceled"):
            pi_id = obj.get("id")
            payment_row = None
            if pi_id:
                result = await session.execute(select(Payment).where(Payment.provider_object_id == pi_id))
                payment_row = result.scalars().first()
            if payment_row:
                if event_type.endswith("succeeded"):
                    payment_row.status = "succeeded"
                    payment_row.completed_at = datetime.utcnow()
                    payment_row.failure_reason = None
                elif event_type.endswith("canceled"):
                    payment_row.status = "canceled"
                    payment_row.completed_at = datetime.utcnow()
                else:
                    payment_row.status = "failed"
                    err = obj.get("last_payment_error") or {}
                    payment_row.failure_reason = str(err.get("message") or err)
                payment_row.updated_at = datetime.utcnow()
                summary["payment_id"] = str(payment_row.id)
                summary["reference_id"] = payment_row.reference_id

        elif event_type == "setup_intent.succeeded":
            si_id = obj.get("id")
            if si_id:
                result = await session.execute(select(Payment).where(Payment.provider_object_id == si_id))
                payment_row = result.scalars().first()
                if payment_row:
                    payment_row.status = "succeeded"
                    payment_row.completed_at = datetime.utcnow()
                    payment_row.updated_at = datetime.utcnow()
                    summary["payment_id"] = str(payment_row.id)

        elif event_type == "account.updated":
            acct_id = obj.get("id")
            if acct_id:
                result = await session.execute(
                    select(ConnectAccount).where(ConnectAccount.stripe_account_id == acct_id)
                )
                account = result.scalars().first()
                if account:
                    account.charges_enabled = bool(obj.get("charges_enabled", False))
                    account.updated_at = datetime.utcnow()
                    summary["nutritionist_id"] = account.nutritionist_id
                    summary["charges_enabled"] = account.charges_enabled

        if event_id:
            result = await session.execute(
                select(WebhookEvent).where(WebhookEvent.stripe_event_id == event_id)
            )
            hook = result.scalars().first()
            if hook:
                hook.processed = True
                hook.processed_at = datetime.utcnow()

        await session.commit()
        return summary
    except Exception as e:
        print(f"[PaymentStore] apply_webhook_event skipped: {e}")
        if session:
            await session.rollback()
        return {"status": "ok", "event_type": event_type, "persisted": False}
    finally:
        if close and session:
            await session.close()


async def _save(entity, db: Optional[AsyncSession]):
    session = db
    close = False
    try:
        if session is None:
            session = AsyncSessionLocal()
            close = True
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity
    except Exception as e:
        print(f"[PaymentStore] persist skipped (Postgres offline?): {e}")
        if session:
            await session.rollback()
        return None
    finally:
        if close and session:
            await session.close()
