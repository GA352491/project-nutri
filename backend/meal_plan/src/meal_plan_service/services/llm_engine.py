import json
import os
import logging
from typing import Dict, Any, List

from nutriplan_shared.service_registry import DEFAULT_LLM_MODEL
from nutriplan_shared.llm import llm_chat

logger = logging.getLogger("meal_plan.llm_engine")


class LLMEngine:
    def __init__(self, model: str = DEFAULT_LLM_MODEL):
        self.model = model

    async def generate_meal_plan(
        self, 
        user_profile: Dict[str, Any], 
        pantry_items: List[str], 
        target_calories: int
    ) -> Dict[str, Any]:
        """
        Calls LiteLLM (defaulting to local Ollama) to generate a structured meal plan.
        Forces JSON output format.
        """
        system_prompt = f"""
You are a world-class AI nutritionist. Your task is to generate a 1-day meal plan based on the following constraints.
Target Calories: {target_calories} kcal (+/- 10%)
Dietary Preferences: {user_profile.get('diet', 'Omnivore')}
Available Pantry Items: {', '.join(pantry_items) if pantry_items else 'None specified'}

IMPORTANT RULES:
1. Try to utilize the Available Pantry Items as much as possible to reduce food waste.
2. Ensure the meals are realistic and easy to cook.
3. You MUST respond with ONLY a valid JSON object. Do not include markdown code blocks, do not include any other text.
4. The JSON must exactly match this schema:
{{
  "meals": [
    {{
      "type": "Breakfast|Lunch|Dinner|Snack",
      "name": "Meal Name",
      "ingredients": [
        {{"name": "Ingredient Name", "amount": "1 cup", "in_pantry": true}}
      ],
      "instructions": ["Step 1", "Step 2"],
      "macros": {{
        "calories": 400,
        "protein": 20,
        "carbs": 40,
        "fat": 15
      }}
    }}
  ],
  "daily_total_macros": {{
    "calories": 1950,
    "protein": 110,
    "carbs": 200,
    "fat": 65
  }}
}}
"""
        try:
            content = await llm_chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Generate the meal plan now in strict JSON."}
                ],
                model=self.model,
                temperature=0.2,
                max_tokens=1500,
                response_format={"type": "json_object"},
                timeout=120.0
            )

            # Strip markdown code blocks if the model wrapped output
            clean_content = content.strip()
            if clean_content.startswith("```json"):
                clean_content = clean_content[7:]
            elif clean_content.startswith("```"):
                clean_content = clean_content[3:]
            if clean_content.endswith("```"):
                clean_content = clean_content[:-3]
            clean_content = clean_content.strip()

            return json.loads(clean_content)

        except Exception as e:
            logger.error(f"Error calling LiteLLM for meal plan generation: {e}")
            return {"meals": [], "error": str(e)}


llm_engine = LLMEngine()
