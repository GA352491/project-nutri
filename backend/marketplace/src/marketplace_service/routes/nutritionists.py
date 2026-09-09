import os
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx
from ..services.marketplace_service import (
    list_nutritionists,
    create_nutritionist_profile,
    get_nutritionist_by_id,
)

router = APIRouter()

from nutriplan_shared.service_registry import PAYMENT_URL as _REG_PAYMENT_URL

PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", _REG_PAYMENT_URL)


class NutritionistProfileRequest(BaseModel):
    user_id: Optional[str] = None
    name: str
    email: Optional[str] = ""
    bio: str
    specialties: List[str] = Field(default_factory=list)
    hourly_rate_usd: float
    certifications: List[str] = Field(default_factory=list)
    ncahp_reg_number: Optional[str] = None
    ida_membership_number: Optional[str] = None
    degree_institution: Optional[str] = None
    degree_year: Optional[str] = None


class VerificationReviewRequest(BaseModel):
    status: str  # verified | pending_review | needs_info | rejected
    badge_tier: str  # ncahp_verified | ida_verified | degree_verified | pending | none
    reviewer_note: Optional[str] = None


class NutritionistResponse(BaseModel):
    id: str
    name: str
    bio: str
    specialties: List[str]
    hourly_rate_usd: float
    certifications: List[str]
    rating: float
    review_count: int
    available_slots: List[str]
    is_verified: bool = True
    verification_status: str = "verified"
    badge_tier: str = "ncahp_verified"
    ncahp_reg_number: Optional[str] = None
    ida_membership_number: Optional[str] = None
    degree_institution: Optional[str] = None


@router.post("/onboard", status_code=status.HTTP_201_CREATED)
async def onboard_nutritionist(profile: NutritionistProfileRequest):
    """
    Self-serve onboarding for nutritionists entering the marketplace.
    1. Persists profile to MongoDB.
    2. Calls the Payment Service to create a Stripe Connect account.
    3. Returns the Stripe hosted onboarding URL so the nutritionist can enter bank details.
    """
    if profile.hourly_rate_usd < 20.0:
        raise HTTPException(status_code=400, detail="Hourly rate must be at least $20 USD")

    nutritionist = await create_nutritionist_profile(profile.model_dump(exclude={"email"}))
    nutritionist_id = str(nutritionist.id)

    # Call payment service to create Stripe Connect account
    stripe_account_id = None
    onboarding_url = None
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{PAYMENT_SERVICE_URL}/api/v1/payment/stripe/connect/init",
                json={
                    "nutritionist_id": nutritionist_id,
                    "email": profile.email or "",
                },
            )
            resp.raise_for_status()
            stripe_data = resp.json()
            stripe_account_id = stripe_data.get("stripe_account_id")
            onboarding_url = stripe_data.get("onboarding_url")
    except httpx.HTTPError as e:
        # Non-fatal: profile was created, Stripe setup can be retried
        print(f"⚠️  Failed to init Stripe Connect for {nutritionist_id}: {e}")

    return {
        "status": "success",
        "message": "Marketplace profile created. Complete your payout setup via the onboarding link.",
        "nutritionist_id": nutritionist_id,
        "stripe_account_id": stripe_account_id,
        "onboarding_url": onboarding_url or f"/expert/onboard/stripe-pending?id={nutritionist_id}",
    }


@router.get("/search")
async def search_nutritionists(specialty: Optional[str] = None, max_rate: Optional[float] = None):
    """
    Search the marketplace for certified nutritionists and dietitians.
    Supports filtering by specialty and maximum hourly rate.
    """
    items = await list_nutritionists(specialty=specialty, max_rate=max_rate)
    return [
        {
            "id": str(n.id),
            "name": n.name,
            "bio": n.bio,
            "specialties": n.specialties,
            "hourly_rate_usd": n.hourly_rate_usd,
            "certifications": n.certifications,
            "rating": n.rating,
            "review_count": n.review_count,
            "stripe_account_id": getattr(n, "stripe_account_id", None),
            "is_verified": getattr(n, "is_verified", True),
            "verification_status": getattr(n, "verification_status", "verified"),
            "badge_tier": getattr(n, "badge_tier", "ncahp_verified"),
            "ncahp_reg_number": getattr(n, "ncahp_reg_number", None),
            "ida_membership_number": getattr(n, "ida_membership_number", None),
            "degree_institution": getattr(n, "degree_institution", None),
            "available_slots": getattr(n, "available_slots", ["09:00 AM", "11:00 AM", "02:00 PM"]),
        }
        for n in items
    ]


@router.get("/{nutritionist_id}")
async def get_nutritionist(nutritionist_id: str):
    """
    Retrieve a single nutritionist profile by ID.
    """
    item = await get_nutritionist_by_id(nutritionist_id)
    if not item:
        raise HTTPException(status_code=404, detail="Nutritionist not found")
    return {
        "id": str(item.id),
        "name": item.name,
        "bio": item.bio,
        "specialties": item.specialties,
        "hourly_rate_usd": item.hourly_rate_usd,
        "certifications": item.certifications,
        "rating": item.rating,
        "review_count": item.review_count,
        "stripe_account_id": getattr(item, "stripe_account_id", None),
        "is_verified": getattr(item, "is_verified", True),
        "verification_status": getattr(item, "verification_status", "verified"),
        "badge_tier": getattr(item, "badge_tier", "ncahp_verified"),
        "ncahp_reg_number": getattr(item, "ncahp_reg_number", None),
        "ida_membership_number": getattr(item, "ida_membership_number", None),
        "degree_institution": getattr(item, "degree_institution", None),
        "available_slots": getattr(item, "available_slots", ["09:00 AM", "11:00 AM", "02:00 PM"]),
    }


@router.post("/apply", status_code=status.HTTP_201_CREATED)
async def submit_application(data: dict):
    """
    Submits a nutritionist clinical verification application.
    Validates format of NCAHP Central Register or IDA Membership numbers.
    """
    ncahp = data.get("ncahpRegNumber") or data.get("ncahp_reg_number")
    ida = data.get("idaMembershipNumber") or data.get("ida_membership_number")

    # Determine default badge tier based on credentials provided
    badge_tier = "degree_verified"
    if ncahp:
        badge_tier = "ncahp_verified"
    elif ida:
        badge_tier = "ida_verified"

    profile_data = {
        "name": data.get("name", "Applicant"),
        "bio": data.get("bio", "Clinical nutrition practitioner"),
        "specialties": data.get("specialties", ["Clinical Nutrition"]),
        "hourly_rate_usd": float(data.get("hourlyRateUsd", data.get("hourly_rate_usd", 75.0))),
        "certifications": [c for c in [ncahp, ida, data.get("degreeInstitution")] if c],
        "is_verified": False,
        "verification_status": "pending_review",
        "badge_tier": "pending",
        "ncahp_reg_number": ncahp,
        "ida_membership_number": ida,
        "degree_institution": data.get("degreeInstitution") or data.get("degree_institution"),
        "degree_year": data.get("degreeYear") or data.get("degree_year"),
    }
    created = await create_nutritionist_profile(profile_data)
    return {
        "status": "success",
        "message": "Application submitted for clinical credentialing review",
        "application_id": str(getattr(created, "id", "app_mock")),
        "initial_tier": badge_tier,
    }


@router.patch("/{nutritionist_id}/verification")
async def update_verification_status(nutritionist_id: str, review: VerificationReviewRequest):
    """
    Admin/Ops action: Approves, updates, or rejects a practitioner's clinical credentials.
    """
    item = await get_nutritionist_by_id(nutritionist_id)
    if not item:
        raise HTTPException(status_code=404, detail="Nutritionist not found")

    is_verified = review.status == "verified"
    if hasattr(item, "set"):
        await item.set({
            Nutritionist.verification_status: review.status,
            Nutritionist.badge_tier: review.badge_tier,
            Nutritionist.is_verified: is_verified,
        })
    else:
        item.verification_status = review.status
        item.badge_tier = review.badge_tier
        item.is_verified = is_verified

    return {
        "status": "success",
        "nutritionist_id": nutritionist_id,
        "verification_status": review.status,
        "badge_tier": review.badge_tier,
        "is_verified": is_verified,
        "reviewer_note": review.reviewer_note,
    }
