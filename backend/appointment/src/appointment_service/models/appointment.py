from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    nutritionist_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    nutritionist_name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    time: Mapped[str] = mapped_column(String(20), nullable=False)
    amount_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), index=True, default="PENDING")
    stripe_account_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    video_room_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
