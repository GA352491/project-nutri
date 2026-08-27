from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uuid
from datetime import datetime

class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    tier: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    provider: str
    cancel_at_period_end: bool
    family_plan_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}

class CheckoutRequest(BaseModel):
    tier: str # premium | pro | family
    success_url: str
    cancel_url: str

class CheckoutResponse(BaseModel):
    checkout_url: str

# Growth Features Schemas: Referrals
class ReferralResponse(BaseModel):
    referral_code: str
    share_url: str
    reward_days: int
    total_referrals: int
    successful_referrals: int

class RedeemReferralRequest(BaseModel):
    referral_code: str

class RedeemReferralResponse(BaseModel):
    status: str
    message: str
    bonus_days_added: int
    new_period_end: datetime

# Growth Features Schemas: Family Plan
class InviteFamilyMemberRequest(BaseModel):
    email: EmailStr

class FamilyInviteResponse(BaseModel):
    id: uuid.UUID
    family_plan_id: uuid.UUID
    invited_email: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

class FamilyPlanDetailsResponse(BaseModel):
    id: uuid.UUID
    primary_user_id: uuid.UUID
    plan_name: str
    max_members: int
    current_member_count: int
    is_active: bool
    invites: List[FamilyInviteResponse] = []

    model_config = {"from_attributes": True}

# Admin Schemas: All Subscriptions & Payments
class AdminSubscriptionItem(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    tier: str
    status: str
    provider: str
    provider_subscription_id: Optional[str] = None
    amount_inr: int
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    family_plan_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}

class AdminSubscriptionListResponse(BaseModel):
    items: List[AdminSubscriptionItem]
    total: int
    page: int
    page_size: int
    total_pages: int
    mrr_inr: int
    active_paid_count: int
    family_plans_count: int

