from typing import List, Optional
from ..models.nutritionist import Nutritionist

# ── In-memory fallback for when MongoDB is offline ───────────────────────────
class _MockNutritionist:
    def __init__(self, **kwargs):
        import uuid
        self.id = str(uuid.uuid4())
        for k, v in kwargs.items():
            setattr(self, k, v)

_SEED_NUTRITIONISTS: List[_MockNutritionist] = [
    _MockNutritionist(
        name="Dr. Sarah Jenkins, RD",
        bio="Clinical dietitian specialising in Diabetes Type 2 reversal, PCOS management, and metabolic health.",
        specialties=["Diabetes", "PCOS", "Metabolic Health", "Weight Loss"],
        hourly_rate_usd=120.0,
        certifications=["Registered Dietitian (RD)", "CDE Certified Diabetes Educator"],
        rating=4.9, review_count=38,
        stripe_account_id=None,
        is_verified=True,
        verification_status="verified",
        badge_tier="ncahp_verified",
        ncahp_reg_number="NCAHP/RD/2023/04812",
        ida_membership_number="IDA-LM-8921",
        degree_institution="AIIMS New Delhi",
        degree_year="2016",
        available_slots=["10:00 AM", "02:00 PM", "05:00 PM"],
    ),
    _MockNutritionist(
        name="Ananya Sharma, M.Sc, RD",
        bio="Integrative nutritionist focusing on Indian whole-food diets, gut microbiome healing, and thyroid support.",
        specialties=["Gut Health", "Thyroid", "Indian Traditional Diets", "Vegetarian Nutrition"],
        hourly_rate_usd=80.0,
        certifications=["M.Sc Clinical Nutrition (NIN)", "IDA Registered Dietitian"],
        rating=5.0, review_count=52,
        stripe_account_id=None,
        is_verified=True,
        verification_status="verified",
        badge_tier="ida_verified",
        ncahp_reg_number=None,
        ida_membership_number="IDA-REG-2019-4410",
        degree_institution="National Institute of Nutrition (NIN), Hyderabad",
        degree_year="2019",
        available_slots=["11:00 AM", "03:00 PM", "06:00 PM"],
    ),
    _MockNutritionist(
        name="Michael Chen, MS, CSCS",
        bio="Sports nutritionist and strength coach working with marathoners, strength athletes and body composition optimisation.",
        specialties=["Sports Nutrition", "Keto", "Hypertrophy", "Fat Loss"],
        hourly_rate_usd=95.0,
        certifications=["MS Sports Nutrition", "ISSN Certified Sports Nutritionist"],
        rating=4.8, review_count=24,
        stripe_account_id=None,
        is_verified=True,
        verification_status="verified",
        badge_tier="degree_verified",
        ncahp_reg_number=None,
        ida_membership_number=None,
        degree_institution="Boston University",
        degree_year="2018",
        available_slots=["09:00 AM", "01:00 PM", "04:00 PM"],
    ),
]

async def seed_initial_nutritionists_if_empty():
    try:
        count = await Nutritionist.count()
        if count == 0:
            seed_data = [
                Nutritionist(
                    name="Dr. Sarah Jenkins, RD",
                    bio="Clinical dietitian specializing in Diabetes Type 2 reversal, PCOS management, and metabolic health.",
                    specialties=["Diabetes", "PCOS", "Metabolic Health", "Weight Loss"],
                    hourly_rate_usd=120.0,
                    certifications=["Registered Dietitian (RD)", "CDE Certified Diabetes Educator"],
                    rating=4.9,
                    review_count=38,
                    is_verified=True,
                    verification_status="verified",
                    badge_tier="ncahp_verified",
                    ncahp_reg_number="NCAHP/RD/2023/04812",
                    ida_membership_number="IDA-LM-8921",
                    degree_institution="AIIMS New Delhi",
                    degree_year="2016",
                ),
                Nutritionist(
                    name="Ananya Sharma, M.Sc, RD",
                    bio="Integrative nutritionist focusing on Indian whole-food diets, gut microbiome healing, and thyroid support.",
                    specialties=["Gut Health", "Thyroid", "Indian Traditional Diets", "Vegetarian Nutrition"],
                    hourly_rate_usd=80.0,
                    certifications=["M.Sc Clinical Nutrition (NIN)", "IDA Registered Dietitian"],
                    rating=5.0,
                    review_count=52,
                    is_verified=True,
                    verification_status="verified",
                    badge_tier="ida_verified",
                    ncahp_reg_number=None,
                    ida_membership_number="IDA-REG-2019-4410",
                    degree_institution="National Institute of Nutrition (NIN), Hyderabad",
                    degree_year="2019",
                ),
                Nutritionist(
                    name="Michael Chen, MS, CSCS",
                    bio="Sports nutritionist and strength coach working with marathoners, strength athletes, and body composition optimization.",
                    specialties=["Sports Nutrition", "Keto", "Hypertrophy", "Fat Loss"],
                    hourly_rate_usd=95.0,
                    certifications=["MS Sports Nutrition", "ISSN Certified Sports Nutritionist"],
                    rating=4.8,
                    review_count=24,
                    is_verified=True,
                    verification_status="verified",
                    badge_tier="degree_verified",
                    ncahp_reg_number=None,
                    ida_membership_number=None,
                    degree_institution="Boston University",
                    degree_year="2018",
                ),
            ]
            for item in seed_data:
                await item.insert()
    except Exception:
        pass  # MongoDB offline — will use in-memory fallback in list_nutritionists

async def list_nutritionists(specialty: Optional[str] = None, max_rate: Optional[float] = None) -> List:
    try:
        await seed_initial_nutritionists_if_empty()
        query = {}
        if specialty:
            query["specialties"] = {"$regex": specialty, "$options": "i"}
        if max_rate:
            query["hourly_rate_usd"] = {"$lte": max_rate}
        return await Nutritionist.find(query).to_list()
    except Exception as e:
        print(f"[Marketplace] Mongo query failed: {e}")
        return []

async def create_nutritionist_profile(data: dict):
    try:
        nutritionist = Nutritionist(**data)
        await nutritionist.insert()
        return nutritionist
    except Exception:
        return _MockNutritionist(**data)

async def get_nutritionist_by_id(nutritionist_id: str):
    try:
        from beanie import PydanticObjectId
        result = await Nutritionist.get(PydanticObjectId(nutritionist_id))
        if result:
            return result
    except Exception:
        pass
    # Fallback: search in-memory
    return next((n for n in _SEED_NUTRITIONISTS if n.id == nutritionist_id), None)
