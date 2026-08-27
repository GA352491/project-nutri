from pydantic import BaseModel
from typing import Optional, List, Literal

# Clinical conditions supported by both IN and US engines
ClinicalCondition = Literal["diabetes", "PCOS", "CKD", "post_partum", "none"]


class UserProfileData(BaseModel):
    age: int
    gender: str
    weight_kg: float
    height_cm: float
    activity_level: str
    is_pregnant: Optional[bool] = False
    is_lactating: Optional[bool] = False
    # Phase 3 additions
    goal: Optional[Literal["lose", "maintain", "gain"]] = "maintain"
    clinical_condition: Optional[ClinicalCondition] = "none"
    region: Optional[Literal["IN", "US"]] = "IN"


class NutrientTarget(BaseModel):
    nutrient: str
    target_value: float
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class ComplianceReport(BaseModel):
    base_bmr: float
    tdee: float
    targets: List[NutrientTarget]
    flags: List[str] = []
    region: str = "IN"
    guideline: str = "ICMR-NIN 2020"
