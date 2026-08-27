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
