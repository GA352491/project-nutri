from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ConnectInitRequest(BaseModel):
    nutritionist_id: str
    email: Optional[str] = ""


class BookingPaymentRequest(BaseModel):
    appointment_id: str
    amount_usd: float
    nutritionist_account_id: str
    metadata: Optional[dict] = None
    user_id: Optional[str] = None


class SetupIntentRequest(BaseModel):
    tier: str
    user_id: Optional[str] = "usr_patient_01"


class PayoutTransferRequest(BaseModel):
    destination_account_id: str
    gross_amount_usd: float
    platform_commission_percent: Optional[float] = 0.15  # Default 15% platform commission, 85% to provider
    currency: Optional[str] = "usd"
    description: Optional[str] = "Telehealth Consultation Payout"
    metadata: Optional[dict] = None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: Optional[str] = None
    purpose: str
    status: str
    amount_cents: int
    currency: str
    platform_fee_cents: int
    provider: str
    provider_object_id: Optional[str] = None
    destination_account_id: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    extra_metadata: Optional[dict] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class ConnectAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nutritionist_id: str
    stripe_account_id: str
    email: Optional[str] = None
    charges_enabled: bool
    created_at: datetime
