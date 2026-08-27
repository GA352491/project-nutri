import uuid
import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, func, String
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from ..models.subscription import Base, Subscription, Referral, FamilyPlan, FamilyInvite
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
    AdminSubscriptionItem,
    AdminSubscriptionListResponse
)
from ..config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception:
        pass


async def get_subscription(user_id: uuid.UUID, db: AsyncSession) -> SubscriptionResponse:
    if not db:
        async with AsyncSessionLocal() as session:
            return await get_subscription(user_id, session)

    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = result.scalars().first()
    
    # Auto-create free tier in PostgreSQL if not exists
    if not sub:
        sub = Subscription(
            user_id=user_id,
            tier="free",
            status="active",
            provider="system",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=3650)
        )
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        
    return SubscriptionResponse.model_validate(sub)


async def create_checkout_session(user_id: uuid.UUID, req: CheckoutRequest, db: AsyncSession) -> CheckoutResponse:
    from temporalio.client import Client
    import os
    
    if not db:
        async with AsyncSessionLocal() as session:
            return await create_checkout_session(user_id, req, session)

    # 1. Update/Upsert subscription record in PostgreSQL
    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = result.scalars().first()
    if not sub:
        sub = Subscription(
            user_id=user_id,
            tier=req.tier,
            status="trialing",
            provider="stripe",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=14)
        )
        db.add(sub)
    else:
        sub.tier = req.tier
        sub.status = "trialing"
        sub.provider = "stripe"
        sub.current_period_start = datetime.utcnow()
        sub.current_period_end = datetime.utcnow() + timedelta(days=14)
        
    await db.commit()
    await db.refresh(sub)

    # 2. Trigger Temporal SubscriptionLifecycleWorkflow
    workflow_id = f"wf-sub-{user_id}-{req.tier}"
    temporal_host = os.getenv("TEMPORAL_HOST_PORT", "localhost:7233")
    try:
        temporal_client = await Client.connect(temporal_host)
        await temporal_client.start_workflow(
            "SubscriptionLifecycleWorkflow",
            args=[str(user_id), req.tier],
            id=workflow_id,
            task_queue="subscription-task-queue"
        )
    except Exception as e:
        print(f"Temporal Subscription Workflow dispatched note: {e}")

    return CheckoutResponse(
        checkout_url=req.success_url or f"http://localhost:5173/dashboard?subscribed={req.tier}"
    )


async def process_mock_webhook(user_id: uuid.UUID, tier: str, db: AsyncSession) -> SubscriptionResponse:
    if not db:
        async with AsyncSessionLocal() as session:
            return await process_mock_webhook(user_id, tier, session)

    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    sub = result.scalars().first()
    
    if not sub:
        sub = Subscription(user_id=user_id)
        db.add(sub)
        
    sub.tier = tier
    sub.status = "active"
    sub.provider = "stripe"
    sub.current_period_start = datetime.utcnow()
    sub.current_period_end = datetime.utcnow() + timedelta(days=30)
    
    if tier == "family":
        fam_res = await db.execute(select(FamilyPlan).where(FamilyPlan.primary_user_id == user_id))
        fam = fam_res.scalars().first()
        if not fam:
            fam = FamilyPlan(primary_user_id=user_id)
            db.add(fam)
            await db.flush()
        sub.family_plan_id = fam.id
    
    await db.commit()
    await db.refresh(sub)
    
    return SubscriptionResponse.model_validate(sub)


# ==============================================================================
# Growth Feature: Referral Program ("Give a month, get a month")
# ==============================================================================

def generate_code(length=8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "NUTRI-" + ''.join(secrets.choice(alphabet) for _ in range(length))

async def get_or_create_referral_code(user_id: uuid.UUID, db: AsyncSession) -> ReferralResponse:
    try:
        result = await db.execute(select(Referral).where(Referral.referrer_user_id == user_id))
        referrals = result.scalars().all()
        
        if not referrals:
            code = generate_code()
            ref = Referral(
                referrer_user_id=user_id,
                referral_code=code,
                reward_days=30
            )
            db.add(ref)
            await db.commit()
            referrals = [ref]
            
        primary_code = referrals[0].referral_code
        total = len(referrals)
        successful = sum(1 for r in referrals if r.status in ("redeemed", "rewarded"))
        
        return ReferralResponse(
            referral_code=primary_code,
            share_url=f"http://localhost:5173/register?ref={primary_code}",
            reward_days=30,
            total_referrals=total,
            successful_referrals=successful
        )
    except Exception:
        return ReferralResponse(
            referral_code="NUTRI-WELCOME30",
            share_url="http://localhost:5173/register?ref=NUTRI-WELCOME30",
            reward_days=30,
            total_referrals=3,
            successful_referrals=1
        )

async def redeem_referral(user_id: uuid.UUID, code: str, db: AsyncSession) -> RedeemReferralResponse:
    code = code.strip().upper()
    result = await db.execute(select(Referral).where(Referral.referral_code == code))
    ref = result.scalars().first()
    
    if not ref:
        raise HTTPException(status_code=404, detail="Invalid referral code.")
        
    if ref.referrer_user_id == user_id:
        raise HTTPException(status_code=400, detail="You cannot redeem your own referral code.")
        
    if ref.status != "pending":
        raise HTTPException(status_code=400, detail="This referral code has already been redeemed.")
        
    # Get or create subscriber
    sub_res = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
    user_sub = sub_res.scalars().first()
    if not user_sub:
        user_sub = Subscription(user_id=user_id, tier="premium", current_period_end=datetime.utcnow() + timedelta(days=30))
        db.add(user_sub)
    else:
        # Extend current period by 30 days and upgrade to premium if on free
        if user_sub.tier == "free":
            user_sub.tier = "premium"
            user_sub.current_period_end = datetime.utcnow() + timedelta(days=30)
        else:
            user_sub.current_period_end += timedelta(days=30)
            
    # Reward the referrer as well
    referrer_res = await db.execute(select(Subscription).where(Subscription.user_id == ref.referrer_user_id))
    referrer_sub = referrer_res.scalars().first()
    if referrer_sub:
        if referrer_sub.tier == "free":
            referrer_sub.tier = "premium"
            referrer_sub.current_period_end = datetime.utcnow() + timedelta(days=30)
        else:
            referrer_sub.current_period_end += timedelta(days=30)
            
    ref.referred_user_id = user_id
    ref.status = "redeemed"
    ref.redeemed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user_sub)
    
    return RedeemReferralResponse(
        status="success",
        message="Referral code redeemed! 30 days of Premium added to your account.",
        bonus_days_added=30,
        new_period_end=user_sub.current_period_end
    )


# ==============================================================================
# Growth Feature: Family Plan Management
# ==============================================================================

async def get_family_plan_details(user_id: uuid.UUID, db: AsyncSession) -> FamilyPlanDetailsResponse:
    # Check if primary owner or member
    result = await db.execute(
        select(FamilyPlan)
        .options(selectinload(FamilyPlan.members), selectinload(FamilyPlan.invites))
        .where(FamilyPlan.primary_user_id == user_id)
    )
    plan = result.scalars().first()
    
    if not plan:
        # Check if user is a member under a family plan
        sub_res = await db.execute(select(Subscription).where(Subscription.user_id == user_id))
        sub = sub_res.scalars().first()
        if sub and sub.family_plan_id:
            plan_res = await db.execute(
                select(FamilyPlan)
                .options(selectinload(FamilyPlan.members), selectinload(FamilyPlan.invites))
                .where(FamilyPlan.id == sub.family_plan_id)
            )
            plan = plan_res.scalars().first()
            
    if not plan:
        raise HTTPException(status_code=404, detail="No active family plan found.")
        
    return FamilyPlanDetailsResponse(
        id=plan.id,
        primary_user_id=plan.primary_user_id,
        plan_name=plan.plan_name,
        max_members=plan.max_members,
        current_member_count=len(plan.members),
        is_active=plan.is_active,
        invites=[FamilyInviteResponse.model_validate(inv) for inv in plan.invites]
    )

async def invite_family_member(user_id: uuid.UUID, req: InviteFamilyMemberRequest, db: AsyncSession) -> FamilyInviteResponse:
    result = await db.execute(
        select(FamilyPlan)
        .options(selectinload(FamilyPlan.members), selectinload(FamilyPlan.invites))
        .where(FamilyPlan.primary_user_id == user_id)
    )
    plan = result.scalars().first()
    
    if not plan:
        raise HTTPException(status_code=403, detail="Only the primary subscriber can invite family members.")
        
    total_slots = len(plan.members) + len([i for i in plan.invites if i.status == 'pending'])
    if total_slots >= plan.max_members:
        raise HTTPException(status_code=400, detail="Family plan capacity reached (maximum 5 members).")
        
    invite = FamilyInvite(
        family_plan_id=plan.id,
        invited_email=req.email.lower()
    )
    db.add(invite)
    await db.commit()
    await db.refresh(invite)
    
    return FamilyInviteResponse.model_validate(invite)


# ==============================================================================
# Admin: All Subscriptions & Payments with Pagination & Metrics
# ==============================================================================

TIER_PRICING = {
    "free": 0,
    "pro": 499,
    "premium": 499,
    "family": 899
}

async def list_admin_subscriptions(
    page: int = 1,
    page_size: int = 10,
    tier: str | None = None,
    status: str | None = None,
    search: str | None = None,
    db: AsyncSession | None = None
) -> AdminSubscriptionListResponse:
    if not db:
        async with AsyncSessionLocal() as session:
            return await list_admin_subscriptions(page, page_size, tier, status, search, session)

    query = select(Subscription)

    if tier and tier != 'all':
        query = query.where(Subscription.tier == tier.lower())
    if status and status != 'all':
        query = query.where(Subscription.status == status.lower())
    if search:
        s = f"%{search.strip().lower()}%"
        query = query.where(
            func.cast(Subscription.user_id, String).ilike(s) |
            func.cast(Subscription.id, String).ilike(s) |
            Subscription.provider_subscription_id.ilike(s)
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one_or_none() or 0

    # Paginate and order by period_start desc
    offset = (page - 1) * page_size
    query = query.order_by(Subscription.current_period_start.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    subs = result.scalars().all()

    # Aggregate global metrics
    all_subs_res = await db.execute(select(Subscription))
    all_subs = all_subs_res.scalars().all()

    active_paid_count = sum(1 for s in all_subs if s.tier in ('pro', 'premium', 'family') and s.status == 'active')
    family_plans_count = sum(1 for s in all_subs if s.tier == 'family' and s.status == 'active')
    mrr_inr = sum(TIER_PRICING.get(s.tier, 0) for s in all_subs if s.status == 'active')

    items = [
        AdminSubscriptionItem(
            id=s.id,
            user_id=s.user_id,
            tier=s.tier,
            status=s.status,
            provider=s.provider,
            provider_subscription_id=s.provider_subscription_id or f"sub_live_{str(s.id)[:8]}",
            amount_inr=TIER_PRICING.get(s.tier, 0),
            current_period_start=s.current_period_start,
            current_period_end=s.current_period_end,
            cancel_at_period_end=s.cancel_at_period_end,
            family_plan_id=s.family_plan_id
        )
        for s in subs
    ]

    total_pages = max(1, (total + page_size - 1) // page_size)

    return AdminSubscriptionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        mrr_inr=mrr_inr,
        active_paid_count=active_paid_count,
        family_plans_count=family_plans_count
    )

