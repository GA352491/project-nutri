"""
India Compliance Rule Engine — ICMR-NIN 2020 Dietary Guidelines.

References:
- ICMR-NIN (2020) Nutrient Requirements for Indians
- National Institute of Nutrition, Hyderabad

Supports:
- Standard healthy adult targets
- Clinical modifications: Diabetes, PCOS, CKD/Renal, Post-partum
"""
from .base import ComplianceRuleEngine
from ..schemas.compliance_schemas import UserProfileData, ComplianceReport, NutrientTarget
from typing import List

ACTIVITY_MULTIPLIERS = {
    "Sedentary":         1.2,
    "Lightly Active":    1.375,
    "Moderately Active": 1.55,
    "Very Active":       1.725,
}


class IndiaICMRRules(ComplianceRuleEngine):
    """
    ICMR-NIN 2020 Guidelines for Indians with clinical condition support.
    """

    def evaluate(self, profile: UserProfileData) -> ComplianceReport:
        # ── 1. BMR (Mifflin-St Jeor) ──────────────────────────────────────────
        if profile.gender.lower() == "male":
            bmr = (10 * profile.weight_kg) + (6.25 * profile.height_cm) - (5 * profile.age) + 5
        else:
            bmr = (10 * profile.weight_kg) + (6.25 * profile.height_cm) - (5 * profile.age) - 161

        multiplier = ACTIVITY_MULTIPLIERS.get(profile.activity_level, 1.2)
        tdee = bmr * multiplier

        # ── 2. Goal-based caloric adjustment ─────────────────────────────────
        goal = getattr(profile, "goal", "maintain") or "maintain"
        if goal == "lose":
            calorie_target = tdee - 400
        elif goal == "gain":
            calorie_target = tdee + 300
        else:
            calorie_target = tdee

        # ── 3. Clinical condition modifications ───────────────────────────────
        condition = getattr(profile, "clinical_condition", "none") or "none"

        # Protein base: 1g/kg (ICMR standard)
        protein_g_per_kg = 1.0
        sugar_max = 50
        sodium_max = 2000   # ICMR recommends <2g sodium/day
        potassium_target = 3500
        fiber_target = 40   # ICMR recommends 40g/day

        if condition == "diabetes":
            protein_g_per_kg = 1.2
            sugar_max = 20          # Strict Indian Diabetes Association limit
        elif condition == "PCOS":
            protein_g_per_kg = 1.2
            sugar_max = 25
        elif condition == "CKD":
            protein_g_per_kg = 0.6  # CKD protein restriction
            sodium_max = 1500
            potassium_target = 2000
            fiber_target = 20
        elif condition == "post_partum":
            protein_g_per_kg = 1.25
            calorie_target += 400   # ICMR post-partum addition

        protein_g = profile.weight_kg * protein_g_per_kg
        protein_cal = protein_g * 4

        # Fat: ~25% of calories (ICMR recommendation)
        fat_pct = 0.25
        fat_cal = calorie_target * fat_pct
        fat_g = fat_cal / 9

        # Carbs: remaining calories
        carb_cal = calorie_target - protein_cal - fat_cal
        if condition in ("diabetes", "PCOS"):
            # Cap carbs at 45% for low-GI approach
            carb_cal = min(carb_cal, calorie_target * 0.45)
        carb_g = carb_cal / 4

        # ── 4. Micronutrients (ICMR-NIN RDA) ─────────────────────────────────
        iron_target = 19 if profile.gender.lower() == "male" else 29
        if getattr(profile, "is_pregnant", False):
            iron_target = 35
        elif condition == "post_partum" or getattr(profile, "is_lactating", False):
            iron_target = 21

        calcium_target = 1000
        if getattr(profile, "is_pregnant", False) or condition == "post_partum":
            calcium_target = 1200

        folate_target = 200
        if getattr(profile, "is_pregnant", False):
            folate_target = 500
        elif condition == "post_partum":
            folate_target = 300

        # ── 5. Compile targets ─────────────────────────────────────────────────
        targets: List[NutrientTarget] = [
            NutrientTarget(nutrient="Calories",       target_value=round(calorie_target), unit="kcal"),
            NutrientTarget(nutrient="Protein",        target_value=round(protein_g),      unit="g"),
            NutrientTarget(nutrient="Fat",            target_value=round(fat_g),          unit="g"),
            NutrientTarget(nutrient="Carbohydrates",  target_value=round(carb_g),         unit="g"),
            NutrientTarget(nutrient="Fiber",          target_value=fiber_target,           unit="g"),
            NutrientTarget(nutrient="Sugar",          target_value=sugar_max,              unit="g", max_value=sugar_max),
            NutrientTarget(nutrient="Sodium",         target_value=sodium_max,             unit="mg", max_value=sodium_max),
            NutrientTarget(nutrient="Potassium",      target_value=potassium_target,       unit="mg"),
            NutrientTarget(nutrient="Iron",           target_value=iron_target,            unit="mg"),
            NutrientTarget(nutrient="Calcium",        target_value=calcium_target,         unit="mg"),
            NutrientTarget(nutrient="Folate",         target_value=folate_target,          unit="mcg"),
            NutrientTarget(nutrient="Vitamin B12",    target_value=2.2,                    unit="mcg"),
            NutrientTarget(nutrient="Zinc",           target_value=12 if profile.gender.lower() == "male" else 10, unit="mg"),
        ]

        # ── 6. Clinical flags ─────────────────────────────────────────────────
        flags = []
        if condition == "diabetes":
            flags.append("DIABETES: Low-GI foods preferred (e.g., millets, legumes). Added sugar <20g. Monitor carbs per meal.")
        if condition == "PCOS":
            flags.append("PCOS: High-protein, low-GI diet. Avoid refined carbs. Include anti-inflammatory spices (turmeric, cinnamon).")
        if condition == "CKD":
            flags.append("CKD/RENAL: Restrict potassium (<2000mg), phosphorus (<800mg), sodium (<1500mg). Limit protein strictly at 0.6g/kg.")
        if condition == "post_partum":
            flags.append("POST-PARTUM: Increased calorie (+400 kcal) and protein targets. Prioritise iron, calcium, and B12.")
        if getattr(profile, "is_pregnant", False):
            flags.append("PREGNANCY: No caloric deficit. Prioritise folate (500mcg/day), iron (35mg/day). Avoid raw fish, papaya.")

        return ComplianceReport(
            base_bmr=round(bmr),
            tdee=round(tdee),
            targets=targets,
            flags=flags,
            region="IN",
            guideline="ICMR-NIN 2020",
        )
