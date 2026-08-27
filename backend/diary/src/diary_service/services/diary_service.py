import uuid
from datetime import date
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, func

from ..models.diary import Base, DiaryEntry, DailySummary
from ..schemas.diary_schemas import (
    LogEntryRequest, DiaryEntryResponse, DailySummaryResponse
)
from ..config import settings

# ── DB session ─────────────────────────────────────────────────────
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── Service logic (Pure PostgreSQL Database Persistence) ───────────
async def log_entry(user_id: uuid.UUID, req: LogEntryRequest, db: AsyncSession) -> DiaryEntryResponse:
    if not db:
        async with AsyncSessionLocal() as session:
            return await log_entry(user_id, req, session)

    new_id = uuid.uuid4()
    entry = DiaryEntry(
        id=new_id,
        user_id=user_id,
        log_date=req.log_date,
        meal_type=req.meal_type,
        food_name=req.food_name,
        quantity_g=req.quantity_g,
        calories=req.calories,
        protein_g=req.protein_g,
        fat_g=req.fat_g,
        carbs_g=req.carbs_g,
        fiber_g=req.fiber_g,
        recipe_id=req.recipe_id,
        source=req.source,
        notes=req.notes,
    )
    db.add(entry)
    await db.flush()

    result = await db.execute(
        select(DailySummary).where(
            (DailySummary.user_id == user_id) &
            (DailySummary.log_date == req.log_date)
        )
    )
    summary = result.scalar_one_or_none()

    if summary:
        summary.total_calories  += req.calories
        summary.total_protein_g += req.protein_g
        summary.total_fat_g     += req.fat_g
        summary.total_carbs_g   += req.carbs_g
        summary.total_fiber_g   += req.fiber_g
        summary.entry_count     += 1
    else:
        summary = DailySummary(
            user_id=user_id,
            log_date=req.log_date,
            total_calories=req.calories,
            total_protein_g=req.protein_g,
            total_fat_g=req.fat_g,
            total_carbs_g=req.carbs_g,
            total_fiber_g=req.fiber_g,
            entry_count=1,
        )
        db.add(summary)

    await db.commit()
    await db.refresh(entry)
    return DiaryEntryResponse.model_validate(entry)


async def get_daily_diary(user_id: uuid.UUID, log_date: date, db: AsyncSession) -> DailySummaryResponse:
    if not db:
        async with AsyncSessionLocal() as session:
            return await get_daily_diary(user_id, log_date, session)

    result = await db.execute(
        select(DailySummary).where(
            (DailySummary.user_id == user_id) &
            (DailySummary.log_date == log_date)
        )
    )
    summary = result.scalar_one_or_none()

    entries_result = await db.execute(
        select(DiaryEntry).where(
            (DiaryEntry.user_id == user_id) &
            (DiaryEntry.log_date == log_date)
        )
    )
    entries = entries_result.scalars().all()

    if not summary:
        return DailySummaryResponse(
            log_date=log_date,
            total_calories=0, total_protein_g=0,
            total_fat_g=0, total_carbs_g=0, total_fiber_g=0,
            entry_count=0,
            entries=[DiaryEntryResponse.model_validate(e) for e in entries]
        )

    return DailySummaryResponse(
        log_date=summary.log_date,
        total_calories=summary.total_calories,
        total_protein_g=summary.total_protein_g,
        total_fat_g=summary.total_fat_g,
        total_carbs_g=summary.total_carbs_g,
        total_fiber_g=summary.total_fiber_g,
        entry_count=summary.entry_count,
        entries=[DiaryEntryResponse.model_validate(e) for e in entries]
    )


async def delete_entry(entry_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> None:
    if not db:
        async with AsyncSessionLocal() as session:
            return await delete_entry(entry_id, user_id, session)

    result = await db.execute(
        select(DiaryEntry).where(
            (DiaryEntry.id == entry_id) & (DiaryEntry.user_id == user_id)
        )
    )
    entry = result.scalar_one_or_none()
    if entry:
        summary_result = await db.execute(
            select(DailySummary).where(
                (DailySummary.user_id == user_id) &
                (DailySummary.log_date == entry.log_date)
            )
        )
        summary = summary_result.scalar_one_or_none()
        if summary:
            summary.total_calories  -= entry.calories
            summary.total_protein_g -= entry.protein_g
            summary.total_fat_g     -= entry.fat_g
            summary.total_carbs_g   -= entry.carbs_g
            summary.total_fiber_g   -= entry.fiber_g
            summary.entry_count     -= 1

        await db.delete(entry)
        await db.commit()

