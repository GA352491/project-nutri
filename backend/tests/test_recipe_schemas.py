import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../recipe/src")))
from recipe_service.schemas.recipe_schemas import CreateRecipeRequest, MacrosInput

def test_create_recipe_request_validation():
    req = CreateRecipeRequest(
        title="Moong Dal Chilla",
        description="High protein savory lentil pancake",
        cuisine="Indian",
        prep_time_minutes=10,
        cook_time_minutes=15,
        instructions=["Grind soaked dal", "Heat pan and spread batter", "Flip and cook until golden"],
        tags=["vegetarian", "high-protein", "breakfast"],
        total_macros=MacrosInput(
            calories_kcal=320,
            protein_g=14,
            fat_g=8,
            carbs_g=45
        )
    )
    assert req.title == "Moong Dal Chilla"
    assert req.total_macros.protein_g == 14
    assert len(req.instructions) == 3
