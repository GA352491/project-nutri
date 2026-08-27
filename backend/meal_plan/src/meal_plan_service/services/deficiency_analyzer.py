"""
Nutritional Deficiency Gap Analyzer & Smart Food Fixer.

Cross-references user's logged 7-day diary or daily intake against ICMR-NIN RDAs:
- Iron: 19 mg/day (Men) / 29 mg/day (Women) [Average reference ~21 mg]
- Calcium: 1000 mg/day
- Fiber: 30 - 40 g/day
- Protein: 0.83 g/kg body weight (Reference ~60 - 80 g/day)
- Vitamin C: 80 mg/day
- Zinc: 12 - 17 mg/day

Generates targeted, culturally authentic regional food fixes and smart supplements.
"""
from typing import Dict, List, Any, Optional
from datetime import date, timedelta
from backend.recipe.src.recipe_service.data.regional_seeds import REGIONAL_RECIPES_SEED


# ICMR-NIN Standard Reference Daily Allowances (RDAs)
ICMR_NIN_RDA = {
    "iron_mg": {"target": 21.0, "unit": "mg", "name": "Iron", "icon": "🩸"},
    "calcium_mg": {"target": 1000.0, "unit": "mg", "name": "Calcium", "icon": "🦴"},
    "fiber_g": {"target": 35.0, "unit": "g", "name": "Dietary Fiber", "icon": "🌾"},
    "protein_g": {"target": 70.0, "unit": "g", "name": "Protein", "icon": "💪"},
    "vitamin_c_mg": {"target": 80.0, "unit": "mg", "name": "Vitamin C", "icon": "🍋"},
    "zinc_mg": {"target": 14.0, "unit": "mg", "name": "Zinc", "icon": "🛡️"},
}


class DeficiencyAnalyzer:
    def __init__(self, catalog: Optional[List[Dict[str, Any]]] = None):
        self.catalog = catalog or REGIONAL_RECIPES_SEED

    def analyze_gap(
        self,
        daily_averages: Dict[str, float],
        regional_preference: str = "in_south_andhra",
        dietary_flag: str = "vegetarian",
    ) -> Dict[str, Any]:
        """
        Compares intake against ICMR-NIN RDA and prescribes authentic regional meal fixes.
        """
        deficiencies = []
        recommendations = []

        for nutrient_key, rda_info in ICMR_NIN_RDA.items():
            actual = daily_averages.get(nutrient_key, 0.0)
            target = rda_info["target"]
            delta = target - actual
            deficit_pct = round((delta / target) * 100, 1)

            if deficit_pct >= 15.0:  # Gap of 15% or more
                severity = "HIGH" if deficit_pct >= 35.0 else "MODERATE"
                deficiencies.append({
                    "nutrient": nutrient_key,
                    "name": rda_info["name"],
                    "icon": rda_info["icon"],
                    "actual": round(actual, 1),
                    "target": target,
                    "unit": rda_info["unit"],
                    "deficit_pct": deficit_pct,
                    "severity": severity,
                })

                # Find the best regional food fix
                best_fix = self._find_food_fix(
                    nutrient_key=nutrient_key,
                    regional_preference=regional_preference,
                    dietary_flag=dietary_flag,
                )
                if best_fix:
                    recommendations.append({
                        "nutrient": rda_info["name"],
                        "icon": rda_info["icon"],
                        "deficit_pct": deficit_pct,
                        "fix_dish": best_fix["title"],
                        "cuisine": best_fix.get("cuisine", "Regional Indian"),
                        "action_message": f"Your {rda_info['name']} is {deficit_pct}% below ICMR-NIN target. Auto-recommending {best_fix['title']}.",
                        "nutrient_provided": f"+{best_fix['nutrient_amount']} {rda_info['unit']} {rda_info['name']}",
                        "calories_kcal": best_fix["calories_kcal"],
                        "meal_slot": best_fix.get("meal_type", "lunch").capitalize(),
                    })

        adherence_score = max(0, min(100, round(100 - (sum(d["deficit_pct"] for d in deficiencies) / len(ICMR_NIN_RDA)))))

        return {
            "status": "analyzed",
            "adherence_score": adherence_score,
            "overall_health_grade": "Optimal" if adherence_score >= 85 else ("Good" if adherence_score >= 70 else "Action Required"),
            "regional_preference": regional_preference,
            "deficiencies_detected": len(deficiencies),
            "deficiencies": deficiencies,
            "actionable_fixes": recommendations,
        }

    def _find_food_fix(
        self,
        nutrient_key: str,
        regional_preference: str,
        dietary_flag: str,
    ) -> Optional[Dict[str, Any]]:
        candidates = []
        for r in self.catalog:
            # Check dietary match
            r_flag = r.get("dietary_flag", "vegetarian").lower()
            df = dietary_flag.lower()
            if df in ["vegetarian", "veg"] and r_flag not in ["vegetarian", "vegan"]:
                continue
            if df == "vegan" and r_flag != "vegan":
                continue

            # Check nutrient density
            amount = 0.0
            if nutrient_key in r.get("total_macros", {}):
                amount = float(r["total_macros"][nutrient_key])
            elif nutrient_key in r.get("total_micros", {}):
                amount = float(r["total_micros"][nutrient_key])

            if amount <= 0:
                continue

            # Prioritize same region
            r_reg = r.get("region_id", "")
            is_same_reg = r_reg.startswith(regional_preference) or regional_preference in r_reg or r_reg == "in_general"
            score = amount * (1.5 if is_same_reg else 1.0)

            candidates.append((score, amount, r))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[0], reverse=True)
        top_recipe = candidates[0][2]
        top_amount = candidates[0][1]

        return {
            "title": top_recipe["title"],
            "cuisine": top_recipe.get("cuisine", "Regional Indian"),
            "meal_type": top_recipe.get("meal_type", "lunch"),
            "nutrient_amount": top_amount,
            "calories_kcal": top_recipe["total_macros"]["calories_kcal"],
        }


deficiency_analyzer = DeficiencyAnalyzer()
