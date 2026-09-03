from fastapi import APIRouter, Depends
from typing import Dict, Any
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.diary_schemas import LogEntryRequest, DiaryEntryResponse, DailySummaryResponse
from ..services.diary_service import log_entry, get_daily_diary, delete_entry, get_db
from nutriplan_shared.auth import get_current_user, user_uuid

router = APIRouter(prefix="/api/v1/diary", tags=["Diary"])


@router.post(
    "/entries",
    response_model=DiaryEntryResponse,
    status_code=201,
    summary="Log a food item",
    description="Logs a single food entry and atomically updates the day's running totals."
)
async def create_entry(
    req: LogEntryRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await log_entry(user_uuid(user), req, db)


@router.get(
    "/day/{log_date}",
    response_model=DailySummaryResponse,
    summary="Get daily diary",
    description="Returns all logged entries and pre-aggregated macro totals for a given date."
)
async def get_day(
    log_date: str,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    cleaned_date = log_date.strip("\"'").lower()
    target_date = date.today() if cleaned_date in ("today", "now") else date.fromisoformat(cleaned_date)
    return await get_daily_diary(user_uuid(user), target_date, db)


@router.get(
    "/compliance/{user_id}",
    summary="Get 7-day diary compliance",
    description="Calculates meal log compliance percentage over the past 7 days for adaptive meal plan adjustments."
)
async def get_compliance(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        uid = uuid.UUID(user_id)
    except Exception:
        return {"user_id": user_id, "days_logged": 0, "compliance_pct": 80.0, "level": "standard", "note": "fallback-id"}

    from datetime import date, timedelta
    from sqlalchemy import select
    from ..models.diary import DailySummary

    start_date = date.today() - timedelta(days=7)
    stmt = select(DailySummary).where(
        (DailySummary.user_id == uid) &
        (DailySummary.log_date >= start_date)
    )
    res = await db.execute(stmt)
    summaries = res.scalars().all()
    days_logged = len(summaries)
    compliance_pct = round((days_logged / 7.0) * 100.0, 1)

    level = "high" if compliance_pct >= 80 else "moderate" if compliance_pct >= 50 else "low"

    return {
        "user_id": user_id,
        "days_logged": days_logged,
        "compliance_pct": compliance_pct,
        "level": level,
        "recommendation": (
            "Progressive calorie/variety advancement" if level == "high" else
            "Maintain current balance" if level == "moderate" else
            "Simplify meal complexity & focus on comfort staples"
        )
    }


@router.delete(
    "/entries/{entry_id}",
    status_code=204,
    summary="Delete a diary entry",
    description="Removes a logged food item and corrects the day's running totals."
)
async def remove_entry(
    entry_id: uuid.UUID,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await delete_entry(entry_id, user_uuid(user), db)

