import pytest
import os
import sys
import asyncio

sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../food_recognition/src")),
])

from food_recognition_service.vision_engine import analyze_image, FOOD_DB, _guess_meal_type

def test_ifct_food_database_coverage():
    """Verify core regional Indian dishes exist with realistic ICMR macros."""
    # South Indian
    assert "pesarattu" in FOOD_DB
    assert FOOD_DB["pesarattu"].protein_g >= 10.0
    assert FOOD_DB["idli"].calories > 100

    # North Indian
    assert "paneer" in FOOD_DB
    assert "rajma" in FOOD_DB
    assert FOOD_DB["rajma"].fiber_g >= 5.0

    # West & East Indian
    assert "thepla" in FOOD_DB
    assert "fish_curry" in FOOD_DB

def test_meal_type_classifier():
    """Verify caloric thresholds map to correct meal tags."""
    assert _guess_meal_type(150) == "snack"
    assert _guess_meal_type(350) == "breakfast"
    assert _guess_meal_type(600) == "lunch"
    assert _guess_meal_type(950) == "dinner"

def test_vision_pipeline_analysis():
    """Verify vision engine returns structured RecognitionResponse with macros."""
    # Test with dummy 1x1 png bytes
    dummy_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    result = asyncio.run(analyze_image(dummy_png, user_region="in_south_andhra"))
    assert result.image_id is not None
    assert len(result.items) > 0
    assert result.total_calories > 0
    assert result.total_protein_g > 0
    assert result.meal_type_guess in ["breakfast", "lunch", "dinner", "snack"]
