import uuid

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from ..schemas.payment_schemas import PaymentResponse
from ..services import payment_store

router = APIRouter()


@router.get("/", response_model=list[PaymentResponse])
async def list_payments(reference_id: Optional[str] = Query(None, description="Appointment, order, or user reference")):
    if not reference_id:
        raise HTTPException(status_code=400, detail="reference_id is required")
    payments = await payment_store.list_payments_by_reference(reference_id)
    return [PaymentResponse.model_validate(p) for p in payments]


@router.get("/provider/{provider_object_id}", response_model=PaymentResponse)
async def get_payment_by_provider_id(provider_object_id: str):
    payment = await payment_store.get_payment_by_provider_id(provider_object_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentResponse.model_validate(payment)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: uuid.UUID):
    payment = await payment_store.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return PaymentResponse.model_validate(payment)
