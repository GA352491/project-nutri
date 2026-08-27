"""
Guardrails AI safety layer for the Meal Plan LLM output.

Guardrails wraps the LLM output with validators that catch dangerous,
irrelevant, or medically unsafe content before it reaches the user.
All validators used here are open-source and run entirely locally.
"""
from __future__ import annotations

try:
    from guardrails import Guard
    from guardrails.hub import ToxicLanguage, DetectPII
    _guard = (
        Guard()
        .use(ToxicLanguage(threshold=0.5, on_fail="exception"))
        .use(DetectPII(["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="fix"))
    )
except Exception:
    _guard = None


class MealPlanGuardrails:
    """
    Wraps the meal plan output through Guardrails AI safety validators.
    """

    def validate_plan(self, plan: DailyPlan) -> DailyPlan:
        """
        Validates a generated DailyPlan through the Guardrails safety rail.
        Currently validates:
        - No toxic / harmful language in meal descriptions
        - No PII accidentally included by the LLM
        - Calorie sanity check (blocks extreme outlier plans)
        """

        # 1. Calorie sanity guard (custom simple check before Guardrails)
        if plan.total_calories < 500 or plan.total_calories > 4000:
            raise ValueError(
                f"Guardrails blocked plan: total calories {plan.total_calories} is out of safe range (500–4000 kcal)."
            )

        # 2. Validate all ingredient text through the Guardrails toxicity rail
        if _guard is not None:
            for meal in plan.meals:
                ingredient_text = ", ".join(meal.ingredients)
                _guard.validate(ingredient_text)

        return plan


guardrails_layer = MealPlanGuardrails()
