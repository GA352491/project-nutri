import pytest
import os
import sys
import asyncio

sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../recipe/src")),
])

from recipe_service.services.external_food_connector import live_external_food_connector

def test_live_external_recipe_search_live_api():
    """Verify live search directly fetches recipes from 3rd-party public APIs and computes ICMR macros."""
    # Test query for Indian chicken dishes
    results = asyncio.run(live_external_food_connector.search_live_recipes(query="chicken", cuisine="Indian", limit=5))
    
    assert isinstance(results, list)
    assert len(results) > 0
    
    first = results[0]
    assert "title" in first
    assert "cuisine" in first
    assert "ingredients" in first
    assert "macros" in first
    
    # Check that macros are dynamically calculated
    macros = first["macros"]
    assert macros["calories_kcal"] > 0
    assert macros["protein_g"] > 0
    assert macros["carbs_g"] >= 0
    assert macros["fat_g"] >= 0
    assert macros["calcium_mg"] >= 0
    assert macros["iron_mg"] >= 0

def test_live_nutrient_computation_engine():
    """Verify ICMR nutrient density computation calculates realistic macros from raw ingredients."""
    title = "Paneer Palak Bhurji"
    ingredients = ["200g Fresh Paneer", "150g Chopped Palak Spinach", "1 tsp Cumin", "1 tbsp Ghee"]
    
    macros = live_external_food_connector.compute_recipe_nutrients(title, ingredients, servings=1)
    
    # Paneer + Palak should result in high calcium, high protein, and high iron
    assert macros["protein_g"] >= 15.0
    assert macros["calcium_mg"] >= 200.0
    assert macros["iron_mg"] >= 3.0
    assert macros["calories_kcal"] > 250.0
