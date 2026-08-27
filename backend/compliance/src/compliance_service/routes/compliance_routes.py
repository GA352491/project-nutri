from fastapi import APIRouter
from ..schemas.compliance_schemas import UserProfileData, ComplianceReport
from ..services.compliance_engine import get_engine

router = APIRouter(prefix="/api/v1/compliance", tags=["Compliance"])


@router.post(
    "/evaluate",
    response_model=ComplianceReport,
    summary="Evaluate profile against nutritional guidelines",
    description=(
        "Takes user demographic data and returns personalised macro/micronutrient targets. "
        "Supports regions: IN (ICMR-NIN 2020) and US (USDA DGA 2020-2025 / FDA DVs). "
        "Clinical conditions supported: diabetes, PCOS, CKD, post_partum."
    ),
)
async def evaluate_profile(profile_data: UserProfileData):
    """
    Dispatches to the correct regional engine (IN or US) based on profile.region,
    applies clinical condition modifications, and returns a full ComplianceReport.
    """
    region = profile_data.region or "IN"
    engine = get_engine(region=region)
    return engine.generate_report(profile_data)


@router.get(
    "/regions",
    summary="List supported regions and guidelines",
)
async def list_regions():
    """Returns the regions and clinical conditions supported by the compliance engine."""
    return {
        "regions": {
            "IN": {
                "name": "India",
                "guideline": "ICMR-NIN Nutrient Requirements for Indians (2020)",
                "authority": "National Institute of Nutrition, Hyderabad",
            },
            "US": {
                "name": "United States",
                "guideline": "USDA Dietary Guidelines for Americans 2020-2025 + FDA Daily Values (21 CFR 101.9)",
                "authority": "USDA / FDA",
            },
        },
        "clinical_conditions": [
            {"id": "none",       "label": "None (healthy adult)"},
            {"id": "diabetes",   "label": "Type 2 Diabetes / Pre-diabetes"},
            {"id": "PCOS",       "label": "Polycystic Ovary Syndrome (PCOS)"},
            {"id": "CKD",        "label": "Chronic Kidney Disease (CKD/Renal Diet)"},
            {"id": "post_partum","label": "Post-partum / Lactating"},
        ],
    }
