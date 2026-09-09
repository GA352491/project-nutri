from beanie import Document
from pydantic import Field
from typing import List, Optional
from datetime import datetime

class Nutritionist(Document):
    user_id: Optional[str] = None
    name: str = Field(indexed=True)
    bio: str
    specialties: List[str] = Field(default_factory=list)
    hourly_rate_usd: float
    certifications: List[str] = Field(default_factory=list)
    rating: float = 4.8
    review_count: int = 12
    stripe_account_id: Optional[str] = None
    is_verified: bool = True
    verification_status: str = "verified"  # verified | pending_review | needs_info | rejected | unverified
    badge_tier: str = "ncahp_verified"     # ncahp_verified | ida_verified | degree_verified | pending | none
    ncahp_reg_number: Optional[str] = None
    ida_membership_number: Optional[str] = None
    degree_institution: Optional[str] = None
    degree_year: Optional[str] = None
    available_slots: List[str] = Field(default_factory=lambda: ["09:00 AM", "11:00 AM", "02:00 PM", "04:30 PM"])
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "marketplace_nutritionists"
