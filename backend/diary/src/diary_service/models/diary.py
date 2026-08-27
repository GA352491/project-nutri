from sqlalchemy import String, Date, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import date

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class DiaryEntry(Base):
    """One entry = one logged food item or meal."""
    __tablename__ = "diary_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)  # breakfast|lunch|snack|dinner

    # Source of entry
    source: Mapped[str] = mapped_column(String(20), default="manual")   # manual | photo | plan
    recipe_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    food_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Portion & macro snapshot
    quantity_g: Mapped[float] = mapped_column(Float, default=100.0)
    calories: Mapped[float] = mapped_column(Float, default=0.0)
    protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    fiber_g: Mapped[float] = mapped_column(Float, default=0.0)

    # Optional photo path (Phase 2 vision)
    photo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class DailySummary(Base):
    """Pre-aggregated daily totals for fast dashboard queries."""
    __tablename__ = "daily_summaries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    total_calories: Mapped[float] = mapped_column(Float, default=0.0)
    total_protein_g: Mapped[float] = mapped_column(Float, default=0.0)
    total_fat_g: Mapped[float] = mapped_column(Float, default=0.0)
    total_carbs_g: Mapped[float] = mapped_column(Float, default=0.0)
    total_fiber_g: Mapped[float] = mapped_column(Float, default=0.0)
    entry_count: Mapped[int] = mapped_column(default=0)
