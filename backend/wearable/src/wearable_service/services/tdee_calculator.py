from typing import Dict, Any

class TDEECalculator:
    """
    Calculates the Total Daily Energy Expenditure dynamically based on
    wearable activity data and user baselines.
    """
    
    def calculate_dynamic_tdee(
        self, 
        profile_bmr: float, 
        wearable_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Takes the base BMR from the user's profile and overrides it with
        the real-time data synced from their wearable (active calories + steps).
        """
        
        # Base BMR (Mifflin-St Jeor calculated at onboarding)
        bmr = profile_bmr
        
        # If the wearable provided its own BMR estimate, we can average it or use it.
        wearable_basal = wearable_data.get("basal_cals", 0)
        if wearable_basal > 0:
            bmr = wearable_basal
            
        active_cals = wearable_data.get("active_cals", 0)
        
        # Fallback: if wearable doesn't provide active calories but gives steps
        steps = wearable_data.get("steps", 0)
        if active_cals == 0 and steps > 0:
            # Rough estimate: ~0.04 calories per step depending on weight/height
            # This is a fallback heuristic.
            active_cals = steps * 0.04
            
        tdee = bmr + active_cals
        
        return {
            "tdee": tdee,
            "bmr_used": bmr,
            "active_cals_used": active_cals,
            "steps": steps,
            "source": wearable_data.get("source", "Calculation")
        }

tdee_calculator = TDEECalculator()
