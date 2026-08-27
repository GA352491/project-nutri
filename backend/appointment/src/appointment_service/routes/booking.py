from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession

from ..services import appointment_store

router = APIRouter()

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST_PORT", "localhost:7233")
TEMPORAL_TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "booking-task-queue")


class TimeSlot(BaseModel):
    time: str
    available: bool


class AppointmentRequest(BaseModel):
    nutritionist_id: str
    nutritionist_name: str
    user_id: str
    date: str
    time: str
    amount_usd: float = 100.0
    stripe_account_id: Optional[str] = None


class AppointmentConfirmRequest(BaseModel):
    stripe_payment_intent_id: str
    video_room_url: str
    status: str = "CONFIRMED"


@router.get("")
async def query_appointments(
    nutritionist_id: Optional[str] = None,
    user_id: Optional[str] = None,
    date: Optional[str] = None,
    db: AsyncSession = Depends(appointment_store.get_db),
):
    appts = await appointment_store.list_appointments(
        db, nutritionist_id=nutritionist_id, user_id=user_id, date=date
    )
    return [
        {
            "id": a.id,
            "appointment_id": a.id,
            "patient": a.user_id,
            "user_id": a.user_id,
            "nutritionist_id": a.nutritionist_id,
            "nutritionist_name": a.nutritionist_name,
            "date": a.date,
            "time": a.time,
            "duration": "30m",
            "status": a.status,
            "type": "Nutrition Consultation",
            "amount_usd": a.amount_usd,
            "video_room_url": a.video_room_url or f"/consultation/{a.id}",
        }
        for a in appts
    ]


@router.get("/slots/{nutritionist_id}")
async def get_available_slots(
    nutritionist_id: str,
    date: str,
    db: AsyncSession = Depends(appointment_store.get_db),
) -> List[TimeSlot]:
    slots = await appointment_store.list_slots(db, nutritionist_id, date)
    return [TimeSlot(**s) for s in slots]



@router.post("/book")
async def book_appointment(
    req: AppointmentRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(appointment_store.get_db),
):
    appointment_id = f"apt_{uuid.uuid4().hex[:8]}"
    row = await appointment_store.create_appointment(
        db,
        {
            "id": appointment_id,
            "user_id": req.user_id,
            "nutritionist_id": req.nutritionist_id,
            "nutritionist_name": req.nutritionist_name,
            "date": req.date,
            "time": req.time,
            "amount_usd": req.amount_usd,
            "status": "PENDING",
            "stripe_account_id": req.stripe_account_id,
        },
    )

    async def _trigger_temporal():
        try:
            from temporalio.client import Client
            from appointment_service.temporal_workers.booking_worker import BookingWorkflow

            client = await Client.connect(TEMPORAL_HOST)
            handle = await client.start_workflow(
                BookingWorkflow.run,
                args=[
                    appointment_id,
                    req.user_id,
                    req.amount_usd,
                    req.nutritionist_name,
                    req.stripe_account_id or "",
                ],
                id=f"booking-{appointment_id}",
                task_queue=TEMPORAL_TASK_QUEUE,
            )
            print(f"[BookingAPI] Temporal workflow started: {handle.id}")
        except Exception as e:
            print(f"[BookingAPI] Temporal workflow trigger failed (non-fatal): {e}")

    async def _publish_faststream():
        try:
            from nutriplan_shared.faststream_broker.broker import broker, AppointmentBookedEvent
            async with broker:
                await broker.publish(
                    AppointmentBookedEvent(
                        appointment_id=appointment_id,
                        user_id=req.user_id,
                        nutritionist_id=req.nutritionist_id,
                        amount_usd=req.amount_usd,
                    ),
                    channel="appointment_booked",
                )
        except Exception as e:
            print(f"[BookingAPI] FastStream publish skipped: {e}")

    background_tasks.add_task(_trigger_temporal)
    background_tasks.add_task(_publish_faststream)

    return {
        "status": "pending",
        "appointment_id": row.id,
        "nutritionist_id": row.nutritionist_id,
        "nutritionist_name": row.nutritionist_name,
        "date": row.date,
        "time": row.time,
        "message": "Booking initiated. You will receive a confirmation email with your video link shortly.",
        "temporal_workflow": f"booking-{appointment_id}",
        "temporal_ui": "http://localhost:8233/workflows",
    }


@router.patch("/{appointment_id}/confirm")
async def confirm_appointment(
    appointment_id: str,
    req: AppointmentConfirmRequest,
    db: AsyncSession = Depends(appointment_store.get_db),
):
    row = await appointment_store.confirm_appointment(
        db,
        appointment_id,
        req.stripe_payment_intent_id,
        req.video_room_url,
        req.status,
    )
    return {
        "status": "ok",
        "appointment_id": row.id,
        "confirmed_status": row.status,
        "video_room_url": row.video_room_url,
        "stripe_payment_intent_id": row.stripe_payment_intent_id,
    }


@router.get("/{appointment_id}")
async def get_appointment(
    appointment_id: str,
    db: AsyncSession = Depends(appointment_store.get_db),
):
    appt = await appointment_store.get_appointment(db, appointment_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {
        "appointment_id": appt.id,
        "status": appt.status,
        "user_id": appt.user_id,
        "nutritionist_id": appt.nutritionist_id,
        "nutritionist_name": appt.nutritionist_name,
        "date": appt.date,
        "time": appt.time,
        "amount_usd": appt.amount_usd,
        "stripe_payment_intent_id": appt.stripe_payment_intent_id,
        "video_room_url": appt.video_room_url,
    }
