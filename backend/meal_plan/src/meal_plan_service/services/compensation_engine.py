"""
Smart Cheat Day & Calorie Budget Compensation Engine.

Detects meal/day overages and provides two scientifically balanced recovery strategies:
1. 'smooth_48h': Deducts the overage evenly over the next 2 days (-100 to -200 kcal/day),
   preserving lean protein while adjusting refined carbs & cooking oils.
2. 'forgive_cheat_day': Keeps the weekly baseline untouched, logging it as an authorized recharge day.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class CompensationRequest(BaseModel):
    user_id: str
    target_calories: int = 1800
    logged_calories: int = 2250
    overage_reason: Optional[str] = "Outside Restaurant / Social Dining"
    strategy: str = "smooth_48h"  # 'smooth_48h' | 'forgive_cheat_day'
    days_to_spread: int = 2


class CompensationPlanResponse(BaseModel):
    user_id: str
    overage_kcal: int
    strategy: str
    daily_adjustment_kcal: int
    adjusted_targets_next_days: List[Dict[str, Any]]
    clinical_notes: str
    macro_guidance: Dict[str, str]


class CalorieCompensationEngine:
    def evaluate_overage(self, target_kcal: int, logged_kcal: int) -> Dict[str, Any]:
        delta = logged_kcal - target_kcal
        is_significant = delta >= 250
        return {
            "has_overage": delta > 50,
            "is_significant": is_significant,
            "overage_kcal": max(0, delta),
            "percentage_over": round((delta / max(1, target_kcal)) * 100, 1) if delta > 0 else 0.0,
            "recommended_action": "smooth_48h" if is_significant else "minor_adjustment"
        }

    def generate_compensation_plan(self, req: CompensationRequest) -> CompensationPlanResponse:
        overage = max(0, req.logged_calories - req.target_calories)

        if req.strategy == "forgive_cheat_day" or overage == 0:
            return CompensationPlanResponse(
                user_id=req.user_id,
                overage_kcal=overage,
                strategy="forgive_cheat_day",
                daily_adjustment_kcal=0,
                adjusted_targets_next_days=[
                    {"day_offset": 1, "target_kcal": req.target_calories, "adjustment": 0},
                    {"day_offset": 2, "target_kcal": req.target_calories, "adjustment": 0}
                ],
                clinical_notes="Cheat meal absorbed as metabolic recharge day. Weekly macro baseline remains unaltered.",
                macro_guidance={
                    "protein": "Maintain current baseline (1.2g - 1.6g/kg)",
                    "hydration": "Increase water intake by 500ml to balance sodium retention",
                    "movement": "30-minute brisk walk recommended"
                }
            )

        # Smooth 48h compensation
        days = max(1, min(req.days_to_spread, 3))
        # Cap daily reduction to maximum 250 kcal/day to prevent metabolic crash or binge cycles
        daily_reduction = min(250, int(overage / days))
        adjusted_target = max(1300, req.target_calories - daily_reduction)

        schedule = []
        for d in range(1, days + 1):
            schedule.append({
                "day_offset": d,
                "target_kcal": adjusted_target,
                "reduction_kcal": daily_reduction,
                "focus": "Low-GI high-fiber greens with normal protein"
            })

        return CompensationPlanResponse(
            user_id=req.user_id,
            overage_kcal=overage,
            strategy="smooth_48h",
            daily_adjustment_kcal=-daily_reduction,
            adjusted_targets_next_days=schedule,
            clinical_notes=(
                f"Recovering {overage} kcal overage smoothly across {days} days (-{daily_reduction} kcal/day). "
                "Protein target is preserved; reductions applied to refined starch & cooking oils."
            ),
            macro_guidance={
                "protein": "PROTECTED: Keep full protein portions (Paneer/Soya/Chicken/Dal)",
                "carbohydrates": "Reduce rice/roti portion by 25% for lunch & dinner",
                "fats": "Minimize tadka & cooking oils (substitute with steamed/roasted preparation)",
                "fiber": "Double leafy greens and kachumber salad to maintain satiety"
            }
        )


compensation_engine = CalorieCompensationEngine()
