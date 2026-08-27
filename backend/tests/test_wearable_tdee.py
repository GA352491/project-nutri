import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../wearable/src")))
from wearable_service.services.tdee_calculator import tdee_calculator

def test_dynamic_tdee_with_active_calories():
    profile_bmr = 1600.0
    wearable_data = {
        "active_cals": 450,
        "steps": 8500,
        "source": "Apple Health"
    }
    result = tdee_calculator.calculate_dynamic_tdee(profile_bmr, wearable_data)
    assert result["tdee"] == 2050.0
    assert result["active_cals_used"] == 450
    assert result["source"] == "Apple Health"

def test_dynamic_tdee_fallback_steps():
    profile_bmr = 1500.0
    wearable_data = {
        "active_cals": 0,
        "steps": 10000,
        "source": "Google Fit"
    }
    result = tdee_calculator.calculate_dynamic_tdee(profile_bmr, wearable_data)
    # 10,000 steps * 0.04 = 400 active cals
    assert result["tdee"] == 1900.0
    assert result["active_cals_used"] == 400.0

def test_dynamic_tdee_wearable_basal_override():
    profile_bmr = 1500.0
    wearable_data = {
        "basal_cals": 1650.0,
        "active_cals": 300,
        "steps": 6000,
        "source": "Garmin"
    }
    result = tdee_calculator.calculate_dynamic_tdee(profile_bmr, wearable_data)
    assert result["bmr_used"] == 1650.0
    assert result["tdee"] == 1950.0
