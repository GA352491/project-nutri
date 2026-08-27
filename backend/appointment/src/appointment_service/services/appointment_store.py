from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..config import settings
from ..models.appointment import Appointment, Base

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

DEFAULT_SLOTS = ["09:00 AM", "10:30 AM", "02:00 PM", "04:15 PM"]


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def list_slots(db: AsyncSession, nutritionist_id: str, day: str) -> list[dict]:
    taken = await db.execute(
        select(Appointment.time).where(
            Appointment.nutritionist_id == nutritionist_id,
            Appointment.date == day,
            Appointment.status.in_(("PENDING", "CONFIRMED")),
        )
    )
    booked = {row[0] for row in taken.all()}
    return [{"time": t, "available": t not in booked} for t in DEFAULT_SLOTS]


async def create_appointment(db: AsyncSession, data: dict) -> Appointment:
    row = Appointment(**data)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def confirm_appointment(
    db: AsyncSession,
    appointment_id: str,
    stripe_payment_intent_id: str,
    video_room_url: str,
    status: str = "CONFIRMED",
) -> Appointment:
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    row = result.scalars().first()
    if not row:
        row = Appointment(
            id=appointment_id,
            user_id="unknown",
            nutritionist_id="unknown",
            nutritionist_name="",
            date="",
            time="",
            status=status,
        )
        db.add(row)
    row.status = status
    row.stripe_payment_intent_id = stripe_payment_intent_id
    row.video_room_url = video_room_url
    row.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(row)
    return row


async def get_appointment(db: AsyncSession, appointment_id: str) -> Optional[Appointment]:
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    return result.scalars().first()


async def list_appointments(
    db: AsyncSession,
    nutritionist_id: Optional[str] = None,
    user_id: Optional[str] = None,
    date: Optional[str] = None,
) -> list[Appointment]:
    query = select(Appointment)
    if nutritionist_id:
        query = query.where(Appointment.nutritionist_id == nutritionist_id)
    if user_id:
        query = query.where(Appointment.user_id == user_id)
    if date:
        query = query.where(Appointment.date == date)
    query = query.order_by(Appointment.date.desc(), Appointment.time.asc())
    result = await db.execute(query)
    return list(result.scalars().all())

