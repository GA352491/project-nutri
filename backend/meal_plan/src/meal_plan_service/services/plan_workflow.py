from typing import Dict, Any, List
from .llm_engine import LLMEngine
from .nutrition_validator import NutritionValidator

class PlanWorkflow:
    def __init__(self):
        self.llm = LLMEngine()
        self.validator = NutritionValidator()

    async def generate_plan_with_retries(
        self, 
        user_id: str, 
        target_calories: int, 
        user_profile: Dict[str, Any], 
        pantry_items: List[str],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Orchestrates the LLM generation and validation loop.
        If validation fails, it retries up to max_retries.
        """
        
        last_error = ""
        
        for attempt in range(max_retries):
            # 1. Generate Plan
            llm_plan = await self.llm.generate_meal_plan(
                user_profile=user_profile,
                pantry_items=pantry_items,
                target_calories=target_calories
            )
            
            # Check for API/Network errors
            if "error" in llm_plan:
                last_error = llm_plan["error"]
                print(f"Attempt {attempt+1} failed due to API error: {last_error}")
                continue
                
            # 2. Validate Plan Math & Bounds
            is_valid, reason = self.validator.validate_plan(llm_plan, target_calories)
            
            if is_valid:
                print(f"Plan generated successfully on attempt {attempt+1}!")
                # 3. Enhance plan with our DB IDs, cache in Redis, etc. (Skipped for brevity)
                return llm_plan
            else:
                last_error = reason
                print(f"Attempt {attempt+1} failed validation: {reason}")
                # We could append this error to the next LLM prompt to tell it what it did wrong
                
        # 4. Fallback (If all retries fail, return a curated fallback)
        print("All LLM attempts failed. Falling back to Curated Engine.")
        return self._get_fallback_curated_plan(target_calories, user_profile)
        
    def _get_fallback_curated_plan(self, target_calories: int, profile: Dict) -> Dict:
        """
        Returns a safe, pre-calculated meal plan from the database.
        """
        # In a real implementation, this would call curated_engine.py
        return {
            "is_fallback": True,
            "meals": [
                {
                    "type": "Lunch",
                    "name": "Standard Chicken & Rice",
                    "macros": {"calories": 600, "protein": 40, "carbs": 60, "fat": 20}
                }
            ],
            "daily_total_macros": {"calories": 600, "protein": 40, "carbs": 60, "fat": 20}
        }

workflow_engine = PlanWorkflow()
