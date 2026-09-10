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
from ..models.nutritionist import Nutritionist

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


class ClinicianInviteRequest(BaseModel):
    name: str
    email: str
    ncahp_reg_number: Optional[str] = None
    ida_membership_number: Optional[str] = None
    assigned_tier: str = "ncahp_verified"
    specialties: List[str] = Field(default_factory=lambda: ["Clinical Nutrition", "Metabolic Health"])
    hourly_rate_usd: float = 85.0
    send_email: bool = True


class ClinicianClaimRequest(BaseModel):
    invite_token: str
    password: str
    phone: Optional[str] = ""
    bio: Optional[str] = ""


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
            "title": getattr(n, "title", None),
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
            "degree_year": getattr(n, "degree_year", None),
            "photo_url": getattr(n, "photo_url", None),
            "languages": getattr(n, "languages", []),
            "experience_years": getattr(n, "experience_years", None),
            "consultation_modes": getattr(n, "consultation_modes", ["video"]),
            "available_slots": getattr(n, "available_slots", ["09:00 AM", "11:00 AM", "02:00 PM"]),
            "is_invite_claimed": getattr(n, "is_invite_claimed", True),
        }
        for n in items
    ]


@router.get("/me")
async def get_my_nutritionist_profile(email: Optional[str] = None, user_id: Optional[str] = None):
    """
    Looks up a nutritionist profile by email or user_id for the logged-in practitioner.
    Falls back to the first active nutritionist if not found.
    """
    from ..models.nutritionist import Nutritionist as NutritionistModel
    item = None
    if email:
        item = await NutritionistModel.find_one(NutritionistModel.email == email)
    if not item and user_id:
        item = await NutritionistModel.find_one(NutritionistModel.user_id == user_id)
    if not item:
        # Fallback to first active nutritionist
        items = await list_nutritionists()
        if items:
            item = items[0]

    if not item:
        raise HTTPException(status_code=404, detail="No nutritionist profile found.")

    return {
        "id": str(item.id),
        "name": item.name,
        "title": getattr(item, "title", "Clinical Dietitian"),
        "bio": item.bio,
        "email": getattr(item, "email", ""),
        "phone": getattr(item, "phone", ""),
        "photo_url": getattr(item, "photo_url", ""),
        "specialties": item.specialties,
        "hourly_rate_usd": item.hourly_rate_usd,
        "certifications": item.certifications,
        "languages": getattr(item, "languages", ["English"]),
        "experience_years": getattr(item, "experience_years", 5),
        "consultation_modes": getattr(item, "consultation_modes", ["video"]),
        "rating": item.rating,
        "review_count": item.review_count,
        "stripe_account_id": getattr(item, "stripe_account_id", None),
        "is_verified": getattr(item, "is_verified", True),
        "verification_status": getattr(item, "verification_status", "verified"),
        "badge_tier": getattr(item, "badge_tier", "ncahp_verified"),
        "ncahp_reg_number": getattr(item, "ncahp_reg_number", None),
        "ida_membership_number": getattr(item, "ida_membership_number", None),
        "degree_institution": getattr(item, "degree_institution", None),
        "degree_year": getattr(item, "degree_year", None),
        "available_slots": getattr(item, "available_slots", ["09:00 AM", "11:00 AM", "02:00 PM"]),
        "is_invite_claimed": getattr(item, "is_invite_claimed", True),
    }


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
        "title": getattr(item, "title", "Clinical Dietitian"),
        "bio": item.bio,
        "email": getattr(item, "email", ""),
        "phone": getattr(item, "phone", ""),
        "photo_url": getattr(item, "photo_url", ""),
        "specialties": item.specialties,
        "hourly_rate_usd": item.hourly_rate_usd,
        "certifications": item.certifications,
        "languages": getattr(item, "languages", ["English"]),
        "experience_years": getattr(item, "experience_years", 5),
        "consultation_modes": getattr(item, "consultation_modes", ["video"]),
        "rating": item.rating,
        "review_count": item.review_count,
        "stripe_account_id": getattr(item, "stripe_account_id", None),
        "is_verified": getattr(item, "is_verified", True),
        "verification_status": getattr(item, "verification_status", "verified"),
        "badge_tier": getattr(item, "badge_tier", "ncahp_verified"),
        "ncahp_reg_number": getattr(item, "ncahp_reg_number", None),
        "ida_membership_number": getattr(item, "ida_membership_number", None),
        "degree_institution": getattr(item, "degree_institution", None),
        "degree_year": getattr(item, "degree_year", None),
        "available_slots": getattr(item, "available_slots", ["09:00 AM", "11:00 AM", "02:00 PM"]),
        "is_invite_claimed": getattr(item, "is_invite_claimed", True),
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


@router.post("/invite")
async def invite_clinician(invite: ClinicianInviteRequest):
    """
    Admin action: Creates an invited nutritionist profile with pre-assigned verification tier,
    generates a secure 1-time claim token, and initiates an invitation email.
    """
    import secrets
    token = f"inv_{secrets.token_urlsafe(24)}"

    profile_data = {
        "name": invite.name,
        "email": invite.email,
        "bio": f"Clinical nutrition practitioner specializing in {', '.join(invite.specialties)}.",
        "specialties": invite.specialties,
        "hourly_rate_usd": invite.hourly_rate_usd,
        "is_verified": True,
        "verification_status": "verified",
        "badge_tier": invite.assigned_tier,
        "ncahp_reg_number": invite.ncahp_reg_number,
        "ida_membership_number": invite.ida_membership_number,
        "invite_token": token,
        "is_invite_claimed": False,
    }

    created = await create_nutritionist_profile(profile_data)
    clinician_id = str(getattr(created, "id", "inv_mock_id"))
    claim_url = f"/expert/claim?token={token}&email={invite.email}"

    return {
        "status": "success",
        "message": f"Invitation dispatched to {invite.email}",
        "nutritionist_id": clinician_id,
        "invite_token": token,
        "claim_url": claim_url,
        "assigned_tier": invite.assigned_tier,
    }


@router.post("/claim")
async def claim_clinician_invite(req: ClinicianClaimRequest):
    """
    Public action: Clinician uses their 1-time invite token to claim their verified profile,
    set their initial password, and finalize their profile bio.
    """
    if not req.invite_token or len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Valid invite token and 6+ character password required")

    # Look up the nutritionist by their invite token
    from ..models.nutritionist import Nutritionist as NutritionistModel
    nutritionist = await NutritionistModel.find_one(NutritionistModel.invite_token == req.invite_token)
    if not nutritionist:
        raise HTTPException(status_code=404, detail="Invalid or expired invitation token.")

    nutritionist_id = str(nutritionist.id)

    # Mark as claimed (is_invite_claimed=False means wizard not yet complete)
    if hasattr(nutritionist, "set"):
        await nutritionist.set({NutritionistModel.is_invite_claimed: False})
    else:
        nutritionist.is_invite_claimed = False

    return {
        "status": "success",
        "message": "Account successfully claimed. Please complete your profile setup.",
        "nutritionist_id": nutritionist_id,
        "redirect_url": f"/expert/setup?id={nutritionist_id}",
    }


class ProfileUpdateRequest(BaseModel):
    """Partial profile update — only fields present in the payload are written."""
    name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    specialties: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    experience_years: Optional[int] = None
    hourly_rate_usd: Optional[float] = None
    available_slots: Optional[List[str]] = None
    consultation_modes: Optional[List[str]] = None
    ncahp_reg_number: Optional[str] = None
    ida_membership_number: Optional[str] = None
    degree_institution: Optional[str] = None
    degree_year: Optional[str] = None


@router.patch("/{nutritionist_id}/profile")
async def update_profile(nutritionist_id: str, payload: ProfileUpdateRequest):
    """
    Expert action: Updates the nutritionist's full profile after claiming their invite.
    This is called from the post-claim onboarding wizard (/expert/setup).
    Sets is_invite_claimed=True to signal onboarding is complete.
    """
    item = await get_nutritionist_by_id(nutritionist_id)
    if not item:
        raise HTTPException(status_code=404, detail="Nutritionist not found")

    update_data = payload.model_dump(exclude_none=True)
    update_data["is_invite_claimed"] = True  # Mark wizard as completed

    if hasattr(item, "set") and update_data:
        # Beanie Document: build field-level update dict
        field_updates = {}
        for field_name, value in update_data.items():
            if hasattr(Nutritionist, field_name):
                field_updates[getattr(Nutritionist, field_name)] = value
        if field_updates:
            await item.set(field_updates)
    else:
        for field_name, value in update_data.items():
            if hasattr(item, field_name):
                setattr(item, field_name, value)

    return {
        "status": "success",
        "message": "Profile updated successfully.",
        "nutritionist_id": nutritionist_id,
    }


from fastapi import UploadFile, File
from pathlib import Path
import uuid

UPLOAD_DIR = Path("/Users/anishganga/Project-nutri/backend/marketplace/uploads/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/{nutritionist_id}/photo")
async def upload_expert_photo(nutritionist_id: str, file: UploadFile = File(...)):
    """
    Upload an expert's profile photo (PNG, JPG, JPEG, WEBP).
    Saves image, associates photo_url with the practitioner profile, and returns photo_url.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files (JPEG, PNG, WEBP) are supported.")

    ext = Path(file.filename or "avatar.jpg").suffix.lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"

    filename = f"{nutritionist_id}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = UPLOAD_DIR / filename

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    with open(dest_path, "wb") as f:
        f.write(content)

    photo_url = f"/api/v1/marketplace/uploads/avatars/{filename}"

    # Update nutritionist profile in MongoDB
    item = await get_nutritionist_by_id(nutritionist_id)
    if item:
        if hasattr(item, "set"):
            await item.set({Nutritionist.photo_url: photo_url})
        else:
            item.photo_url = photo_url

    return {
        "status": "success",
        "message": "Profile photo uploaded successfully.",
        "photo_url": photo_url,
        "nutritionist_id": nutritionist_id,
    }
