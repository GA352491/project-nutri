import pytest
import sys
import os

# Append shared module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")))
from nutriplan_shared.compliance.india_rules import india_compliance

def test_icmr_compliance_valid_plan():
    plan_macros = {
        "protein_g": 60.0,
        "added_sugar_g": 15.0,
        "sodium_mg": 1400,
        "iron_mg": 18.0
    }
    user_profile = {
        "weight_kg": 65,
        "gender": "male"
    }
    warnings = india_compliance.validate_plan_compliance(plan_macros, user_profile)
    assert len(warnings) == 0

def test_icmr_compliance_excess_sodium():
    plan_macros = {
        "protein_g": 60.0,
        "added_sugar_g": 10.0,
        "sodium_mg": 2500,  # Exceeds 2000mg threshold
        "iron_mg": 15.0
    }
    user_profile = {
        "weight_kg": 65,
        "gender": "male"
    }
    warnings = india_compliance.validate_plan_compliance(plan_macros, user_profile)
    assert len(warnings) == 1
    assert "sodium" in warnings[0].lower()

def test_icmr_compliance_excess_sugar():
    plan_macros = {
        "protein_g": 55.0,
        "added_sugar_g": 35.0,  # Exceeds 25g limit
        "sodium_mg": 1200,
        "iron_mg": 15.0
    }
    user_profile = {
        "weight_kg": 65,
        "gender": "male"
    }
    warnings = india_compliance.validate_plan_compliance(plan_macros, user_profile)
    assert len(warnings) == 1
    assert "sugar" in warnings[0].lower()

def test_icmr_compliance_low_iron_female():
    plan_macros = {
        "protein_g": 55.0,
        "added_sugar_g": 10.0,
        "sodium_mg": 1200,
        "iron_mg": 12.0  # Below 29mg RDA for females
    }
    user_profile = {
        "weight_kg": 55,
        "gender": "female"
    }
    warnings = india_compliance.validate_plan_compliance(plan_macros, user_profile)
    assert any("iron" in w.lower() for w in warnings)
