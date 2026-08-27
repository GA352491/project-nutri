import json
import httpx
from typing import Dict, Any, List

class LLMEngine:
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model = "llama3"

    async def generate_meal_plan(
        self, 
        user_profile: Dict[str, Any], 
        pantry_items: List[str], 
        target_calories: int
    ) -> Dict[str, Any]:
        """
        Calls the local Ollama API to generate a meal plan.
        We force JSON output via prompt engineering and Ollama's json format param.
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

        payload = {
            "model": self.model,
            "prompt": "Generate the meal plan now.",
            "system": system_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2 # Low temperature for more deterministic/calculable outputs
            }
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(f"{self.ollama_host}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                
                # The response from Ollama should be valid JSON string inside the 'response' key
                content = data.get("response", "{}")
                return json.loads(content)
                
            except (httpx.RequestError, json.JSONDecodeError) as e:
                print(f"[!] Error calling Ollama LLM: {str(e)}")
                # Return a fallback/empty plan structure on failure so the workflow can handle it
                return {"meals": [], "error": str(e)}

llm_engine = LLMEngine()
