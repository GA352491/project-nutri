from typing import Dict, Any

class PlanAdjustmentLogic:
    """
    Handles dynamically adjusting the user's remaining daily meal plan targets
    based on real-time wearable activity data.
    """
    
    def adjust_remaining_targets(
        self,
        base_target_cals: int,
        consumed_cals: int,
        wearable_tdee: float,
        goal: str
    ) -> Dict[str, Any]:
        """
        Adjusts the remaining calorie target for the day based on the user's goal
        and how much they've burned according to their wearable.
        """
        
        # Calculate new target based on TDEE and goal
        # If goal is 'Maintain Weight', they should eat exactly their TDEE.
        # If goal is 'Lose Weight', they should eat TDEE - 500 (standard deficit).
        # If goal is 'Gain Muscle', they should eat TDEE + 300 (standard surplus).
        
        dynamic_target = wearable_tdee
        
        if goal == "Lose Weight":
            dynamic_target = wearable_tdee - 500
            # Safety floor: never recommend below 1200 calories (or BMR/some threshold)
            dynamic_target = max(dynamic_target, 1200)
            
        elif goal == "Gain Muscle":
            dynamic_target = wearable_tdee + 300
            
        # Calculate what's remaining to eat today
        remaining = dynamic_target - consumed_cals
        
        # If they've already overeaten their new dynamic target
        if remaining < 0:
            remaining = 0
            
        return {
            "original_base_target": base_target_cals,
            "dynamic_daily_target": int(dynamic_target),
            "consumed_so_far": consumed_cals,
            "remaining_cals": int(remaining),
            "adjustment_reason": f"Activity tracked via wearable modified target by {int(dynamic_target - base_target_cals)} kcal"
        }

plan_adjuster = PlanAdjustmentLogic()
