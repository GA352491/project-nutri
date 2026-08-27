"""
US Compliance Rule Engine — USDA/FDA Dietary Guidelines (2020–2025).

References:
- USDA Dietary Guidelines for Americans 2020–2025 (DGA)
- FDA Daily Values (21 CFR 101.9)
- NIH Office of Dietary Supplements

Handles:
- Standard healthy adult DRI targets
- Clinical modifications: Type 2 Diabetes, PCOS, CKD/Renal, Post-partum
- HIPAA-safe: no PII stored in this module; works on anonymized profile data
"""
from .base import ComplianceRuleEngine
from ..schemas.compliance_schemas import UserProfileData, ComplianceReport, NutrientTarget
from typing import List

# ----- FDA Daily Values (2020) ------------------------------------------------
FDA_DAILY_VALUES = {
    "Sodium":      {"value": 2300,   "unit": "mg",  "max": 2300},
    "Potassium":   {"value": 4700,   "unit": "mg"},
    "Fiber":       {"value": 28,     "unit": "g"},
    "Calcium":     {"value": 1300,   "unit": "mg"},
    "Iron":        {"value": 18,     "unit": "mg"},
    "VitaminD":    {"value": 20,     "unit": "mcg"},
    "Folate":      {"value": 400,    "unit": "mcg"},
    "Cholesterol": {"value": 300,    "unit": "mg",  "max": 300},
    "SaturatedFat":{"value": 20,     "unit": "g",   "max": 20},
    "Sugar":       {"value": 50,     "unit": "g",   "max": 50},
}

# ----- Activity multipliers (Harris-Benedict revision) -----------------------
ACTIVITY_MULTIPLIERS = {
    "Sedentary":          1.2,
    "Lightly Active":     1.375,
    "Moderately Active":  1.55,
    "Very Active":        1.725,
    "Extremely Active":   1.9,
}


class USFDADGARules(ComplianceRuleEngine):
    """
    USDA Dietary Guidelines for Americans 2020–2025 + FDA DVs.
    Applies clinical modifications for: Diabetes, PCOS, CKD, Post-partum.
    """

    def evaluate(self, profile: UserProfileData) -> ComplianceReport:
        # ── 1. TDEE (Mifflin-St Jeor) ────────────────────────────────────────
        if profile.gender.lower() == "male":
            bmr = (10 * profile.weight_kg) + (6.25 * profile.height_cm) - (5 * profile.age) + 5
        else:
            bmr = (10 * profile.weight_kg) + (6.25 * profile.height_cm) - (5 * profile.age) - 161

        multiplier = ACTIVITY_MULTIPLIERS.get(profile.activity_level, 1.375)
        tdee = bmr * multiplier

        # ── 2. Goal-based caloric adjustment ─────────────────────────────────
        goal = getattr(profile, "goal", "maintain")
        if goal == "lose":
            calorie_target = tdee - 500          # ~1 lb/week deficit
        elif goal == "gain":
            calorie_target = tdee + 300
        else:
            calorie_target = tdee

        # ── 3. DGA Macro Distribution ─────────────────────────────────────────
        # Protein: 0.8 g/kg (DGA base), bumped for clinical conditions
        protein_g_per_kg = 0.8
        condition = getattr(profile, "clinical_condition", None)

        if condition in ("diabetes", "PCOS"):
            protein_g_per_kg = 1.2     # higher protein, lower GI carbs
        elif condition == "CKD":
            protein_g_per_kg = 0.6     # renal diet — lower protein
        elif condition == "post_partum":
            protein_g_per_kg = 1.1

        protein_g = profile.weight_kg * protein_g_per_kg
        protein_cal = protein_g * 4

        # Fat: 25–35% of calories (FDA DV uses 78g as reference for 2000 kcal)
        fat_pct = 0.30
        if condition == "CKD":
            fat_pct = 0.35  # allow more fat to compensate reduced protein
        fat_cal = calorie_target * fat_pct
        fat_g = fat_cal / 9

        carb_cal = calorie_target - protein_cal - fat_cal
        carb_g = carb_cal / 4

        # ── 4. Glycemic Index cap for Diabetes / PCOS ──────────────────────────
        sugar_max = 50  # FDA DV default
        sodium_max = 2300
        potassium_target = 4700
        fiber_target = 28

        if condition == "diabetes":
            sugar_max = 25         # ADA recommendation: <25g added sugar
            carb_g = min(carb_g, calorie_target * 0.40 / 4)  # cap carbs at 40%

        elif condition == "PCOS":
            sugar_max = 25
            carb_g = min(carb_g, calorie_target * 0.45 / 4)

        elif condition == "CKD":
            sodium_max = 1500        # NKF Stage 3–4 restriction
            potassium_target = 2000  # restrict potassium
            fiber_target = 20        # moderate only

        elif condition == "post_partum":
            # DRI additions for lactating women
            protein_g += 25          # +25g DRI additional
            calorie_target += 330    # EER addition for lactation

        # ── 5. Gender & life-stage micronutrient overrides ─────────────────────
        iron_target = 8 if profile.gender.lower() == "male" else 18
        if condition == "post_partum" or getattr(profile, "is_lactating", False):
            iron_target = 9
        if getattr(profile, "is_pregnant", False):
            iron_target = 27

        folate_target = 400
        if getattr(profile, "is_pregnant", False) or condition == "post_partum":
            folate_target = 600

        calcium_target = 1000
        if profile.age >= 51 and profile.gender.lower() == "female":
            calcium_target = 1200

        # ── 6. Compile targets list ────────────────────────────────────────────
        targets: List[NutrientTarget] = [
            NutrientTarget(nutrient="Calories",      target_value=round(calorie_target), unit="kcal"),
            NutrientTarget(nutrient="Protein",       target_value=round(protein_g),      unit="g"),
            NutrientTarget(nutrient="Fat",           target_value=round(fat_g),          unit="g",  max_value=round(fat_g * 1.1)),
            NutrientTarget(nutrient="Carbohydrates", target_value=round(carb_g),         unit="g"),
            NutrientTarget(nutrient="Fiber",         target_value=fiber_target,           unit="g"),
            NutrientTarget(nutrient="Sugar",         target_value=sugar_max,              unit="g",  max_value=sugar_max),
            NutrientTarget(nutrient="Sodium",        target_value=sodium_max,             unit="mg", max_value=sodium_max),
            NutrientTarget(nutrient="Potassium",     target_value=potassium_target,       unit="mg"),
            NutrientTarget(nutrient="Calcium",       target_value=calcium_target,         unit="mg"),
            NutrientTarget(nutrient="Iron",          target_value=iron_target,            unit="mg"),
            NutrientTarget(nutrient="Vitamin D",     target_value=20,                     unit="mcg"),
            NutrientTarget(nutrient="Folate",        target_value=folate_target,          unit="mcg"),
            NutrientTarget(nutrient="Saturated Fat", target_value=20,                     unit="g",  max_value=20),
            NutrientTarget(nutrient="Cholesterol",   target_value=300,                    unit="mg", max_value=300),
        ]

        # ── 7. Build flags list ────────────────────────────────────────────────
        flags = []
        if condition == "diabetes":
            flags.append("DIABETES: Low-GI carbs preferred. Added sugar < 25g. Monitor glycemic load per meal.")
        if condition == "PCOS":
            flags.append("PCOS: Low-GI, high-protein diet recommended. Limit refined carbs and trans fats.")
        if condition == "CKD":
            flags.append("CKD/RENAL: Restrict potassium (<2000mg), phosphorus (<800mg), sodium (<1500mg). Monitor protein closely.")
        if condition == "post_partum":
            flags.append("POST-PARTUM: Increased calorie and protein targets. Prioritize iron, calcium, and folate.")
        if getattr(profile, "is_pregnant", False):
            flags.append("PREGNANCY: Do not create caloric deficit. Prioritize folate (600mcg), iron (27mg), DHA (200mg).")

        return ComplianceReport(
            base_bmr=round(bmr),
            tdee=round(tdee),
            targets=targets,
            flags=flags,
            region="US",
            guideline="USDA DGA 2020-2025 / FDA Daily Values",
        )
