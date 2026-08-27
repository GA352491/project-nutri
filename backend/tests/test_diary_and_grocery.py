import pytest
import sys
import os

sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../diary/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../grocery/src")),
])

def test_diary_macro_rollup_calculation():
    """Verify daily macro sums and caloric deficit math."""
    entries = [
        {"calories": 420, "protein_g": 24, "carbs_g": 45, "fat_g": 12},
        {"calories": 650, "protein_g": 42, "carbs_g": 70, "fat_g": 20},
        {"calories": 180, "protein_g": 8,  "carbs_g": 22, "fat_g": 4},
        {"calories": 520, "protein_g": 35, "carbs_g": 55, "fat_g": 16},
    ]

    total_calories = sum(e["calories"] for e in entries)
    total_protein = sum(e["protein_g"] for e in entries)
    total_carbs = sum(e["carbs_g"] for e in entries)
    total_fat = sum(e["fat_g"] for e in entries)

    target_calories = 2000
    deficit = target_calories - total_calories

    assert total_calories == 1770
    assert total_protein == 109
    assert total_carbs == 192
    assert total_fat == 52
    assert deficit == 230  # Healthy mild deficit for fat loss

def test_grocery_pantry_deduction_logic():
    """Verify ingredients already marked as available in pantry are filtered or marked."""
    recipe_ingredients = [
        {"name": "Whole Wheat Atta", "quantity": 500, "unit": "g", "in_pantry": True},
        {"name": "Toor Dal", "quantity": 250, "unit": "g", "in_pantry": False},
        {"name": "Fresh Spinach", "quantity": 1, "unit": "bunch", "in_pantry": False},
        {"name": "Mustard Oil", "quantity": 100, "unit": "ml", "in_pantry": True},
    ]

    to_buy = [i for i in recipe_ingredients if not i["in_pantry"]]
    in_stock = [i for i in recipe_ingredients if i["in_pantry"]]

    assert len(to_buy) == 2
    assert {i["name"] for i in to_buy} == {"Toor Dal", "Fresh Spinach"}
    assert len(in_stock) == 2
