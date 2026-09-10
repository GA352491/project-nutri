"""
Pydantic AI-powered LLM Engine for Meal Plan Generation.

Replaces the raw string-manipulation approach in the original llm_engine.py.
Pydantic AI forces the LLM to return a strict, validated Pydantic schema,
so we never get a malformed JSON response from Ollama.
"""
from __future__ import annotations
import os
from typing import List
from pydantic import BaseModel, Field, field_validator
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel


# ── Strict output schema for the LLM ─────────────────────────────────────────

class MealItem(BaseModel):
    name: str = Field(description="Name of the meal (e.g., 'Moong Dal Khichdi')")
    meal_type: str = Field(description="Breakfast, Lunch, Snack, or Dinner")
    calories: int = Field(ge=50, le=1500, description="Total calories for this meal")
    protein_g: float = Field(ge=0, description="Protein in grams")
    carbs_g: float = Field(ge=0, description="Carbohydrates in grams")
    fat_g: float = Field(ge=0, description="Fat in grams")
    ingredients: List[str] = Field(description="List of key ingredients")

    @field_validator("meal_type")
    @classmethod
    def validate_meal_type(cls, v: str) -> str:
        allowed = {"Breakfast", "Lunch", "Snack", "Dinner"}
        if v not in allowed:
            raise ValueError(f"meal_type must be one of {allowed}")
        return v


class DailyPlan(BaseModel):
    total_calories: int
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    meals: List[MealItem]


# ── Pydantic AI Agent using local Ollama ─────────────────────────────────────

# Ollama exposes an OpenAI-compatible API — URL from env (OLLAMA_URL from service_registry)
try:
    from nutriplan_shared.service_registry import OLLAMA_URL as _OLLAMA_URL
except ImportError:
    _OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

_DEFAULT_MODEL = os.getenv("PYDANTIC_AI_MODEL", "llama3.2:latest")

try:
    _ollama_model = OpenAIChatModel(_DEFAULT_MODEL, base_url=f"{_OLLAMA_URL}/v1", api_key="ollama")
    meal_plan_agent = Agent(
        model=_ollama_model,
        result_type=DailyPlan,
        system_prompt="You are a clinical nutritionist AI. Return ONLY a valid JSON DailyPlan.",
    )
except Exception:
    try:
        _ollama_model = OpenAIChatModel(_DEFAULT_MODEL)
        meal_plan_agent = Agent(model=_ollama_model, result_type=DailyPlan)
    except Exception:
        meal_plan_agent = None


async def generate_plan_with_pydantic_ai(
    caloric_target: int,
    preferences: List[str],
    dietary_restrictions: List[str],
) -> DailyPlan:
    """
    Uses Pydantic AI to invoke the local Ollama model and force-validate
    the output into a DailyPlan schema. No more brittle JSON parsing.
    """
    prompt = (
        f"Create a {caloric_target} kcal daily meal plan. "
        f"Diet preferences: {', '.join(preferences)}. "
        f"Restrictions: {', '.join(dietary_restrictions)}. "
        f"Distribute across Breakfast, Lunch, Snack, and Dinner."
    )
    result = await meal_plan_agent.run(prompt)
    return result.data
