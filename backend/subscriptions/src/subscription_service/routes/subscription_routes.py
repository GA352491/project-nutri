from fastapi import APIRouter, Depends
from typing import Dict, Any
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.subscription_schemas import (
    SubscriptionResponse,
    CheckoutRequest,
    CheckoutResponse,
    ReferralResponse,
    RedeemReferralRequest,
    RedeemReferralResponse,
    InviteFamilyMemberRequest,
    FamilyInviteResponse,
    FamilyPlanDetailsResponse,
    AdminSubscriptionListResponse
)
from ..services.subscription_service import (
    get_subscription,
    create_checkout_session,
    process_mock_webhook,
    get_or_create_referral_code,
    redeem_referral,
    get_family_plan_details,
    invite_family_member,
    list_admin_subscriptions,
    get_db
)
from nutriplan_shared.auth import get_current_user, user_uuid

router = APIRouter(prefix="/api/v1/subscriptions", tags=["Subscriptions"])

@router.get(
    "/me",
    response_model=SubscriptionResponse,
    summary="Get current user's subscription status"
)
async def get_my_subscription(user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_subscription(user_uuid(user), db)

@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    summary="Create a checkout session"
)
async def checkout(req: CheckoutRequest, user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_checkout_session(user_uuid(user), req, db)

@router.post(
    "/mock-webhook",
    response_model=SubscriptionResponse,
    summary="Simulate a successful payment webhook"
)
async def mock_webhook(tier: str, user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await process_mock_webhook(user_uuid(user), tier, db)


# ==============================================================================
# Growth Routes: Referral Program
# ==============================================================================

@router.get(
    "/referrals/my-code",
    response_model=ReferralResponse,
    summary="Get or generate user's referral code"
)
async def get_my_referral_code(user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_or_create_referral_code(user_uuid(user), db)

@router.post(
    "/referrals/redeem",
    response_model=RedeemReferralResponse,
    summary="Redeem a friend's referral code"
)
async def redeem_code(req: RedeemReferralRequest, user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await redeem_referral(user_uuid(user), req.referral_code, db)


# ==============================================================================
# Growth Routes: Family Plans
# ==============================================================================

@router.get(
    "/family/details",
    response_model=FamilyPlanDetailsResponse,
    summary="Get family plan details, members, and invites"
)
async def get_family_details(user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_family_plan_details(user_uuid(user), db)

@router.post(
    "/family/invite",
    response_model=FamilyInviteResponse,
    summary="Invite a family member by email"
)
async def invite_member(req: InviteFamilyMemberRequest, user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await invite_family_member(user_uuid(user), req, db)


# ==============================================================================
# Admin Routes: Payment & Subscription Management
# ==============================================================================

@router.get(
    "/admin/all",
    response_model=AdminSubscriptionListResponse,
    summary="List all user subscriptions and payment records with pagination and search"
)
async def get_all_subscriptions_admin(
    page: int = 1,
    page_size: int = 10,
    tier: str | None = None,
    status: str | None = None,
    search: str | None = None,
    user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await list_admin_subscriptions(
        page=page,
        page_size=page_size,
        tier=tier,
        status=status,
        search=search,
        db=db
    )

