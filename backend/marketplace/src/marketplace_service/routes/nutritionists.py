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

PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8016")


class NutritionistProfileRequest(BaseModel):
    user_id: Optional[str] = None
    name: str
    email: Optional[str] = ""
    bio: str
    specialties: List[str] = Field(default_factory=list)
    hourly_rate_usd: float
    certifications: List[str] = Field(default_factory=list)


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
            "stripe_account_id": n.stripe_account_id,
            "available_slots": n.available_slots,
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
        "stripe_account_id": item.stripe_account_id,
        "available_slots": item.available_slots,
    }
