import pytest
import os
import sys

sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../meal_plan/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../grocery/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../wearable/src")),
])

from meal_plan_service.services.compensation_engine import compensation_engine, CompensationRequest
from meal_plan_service.services.clinical_tracks import clinical_tracks
from grocery_service.services.pantry_recycler import recycle_pantry_ingredients, PantryLeftoverRequest
from wearable_service.routes.ingest import predict_glucose_spike, CGMPredictRequest
import asyncio


def test_smart_cheat_day_compensation_engine():
    """Verify smooth 48-hour calorie reduction preserves protein and spreads overage."""
    req = CompensationRequest(
        user_id="usr_cheat_test",
        target_calories=1800,
        logged_calories=2200,
        strategy="smooth_48h",
        days_to_spread=2
    )
    res = compensation_engine.generate_compensation_plan(req)
    assert res.overage_kcal == 400
    assert res.strategy == "smooth_48h"
    assert len(res.adjusted_targets_next_days) == 2
    assert res.daily_adjustment_kcal == -200
    assert res.adjusted_targets_next_days[0]["target_kcal"] == 1600
    assert "PROTECTED" in res.macro_guidance["protein"]

    # Test forgive cheat day
    req_forgive = CompensationRequest(
        user_id="usr_cheat_test",
        target_calories=1800,
        logged_calories=2400,
        strategy="forgive_cheat_day"
    )
    res_forgive = compensation_engine.generate_compensation_plan(req_forgive)
    assert res_forgive.daily_adjustment_kcal == 0
    assert res_forgive.adjusted_targets_next_days[0]["target_kcal"] == 1800


def test_clinical_risk_preflight_approval_gate():
    """Verify high-risk diabetic and renal profiles trigger mandatory clinical signoff."""
    # High risk profile: Type 1 Diabetes + elevated HbA1c
    high_risk_profile = {
        "user_id": "patient_high_risk",
        "medical_conditions": ["type_1_diabetes", "hypertension"],
        "hba1c": 9.2,
        "serum_creatinine": 1.1
    }
    eval_res = clinical_tracks.evaluate_clinical_risk_gate(high_risk_profile)
    assert eval_res["requires_clinical_signoff"] is True
    assert eval_res["status"] == "STATUS_REQUIRES_CLINICAL_SIGN_OFF"
    assert eval_res["can_auto_assign"] is False
    assert len(eval_res["risk_reasons"]) >= 2

    # Normal profile: General fitness / weight loss
    normal_profile = {
        "user_id": "patient_normal",
        "medical_conditions": ["weight_loss"],
        "hba1c": 5.4,
        "serum_creatinine": 0.8
    }
    normal_eval = clinical_tracks.evaluate_clinical_risk_gate(normal_profile)
    assert normal_eval["requires_clinical_signoff"] is False
    assert normal_eval["status"] == "STATUS_ACTIVE_APPROVED"
    assert normal_eval["can_auto_assign"] is True


def test_pantry_zero_waste_leftover_recycler():
    """Verify fridge leftovers match regional Indian recipes and compute savings."""
    req = PantryLeftoverRequest(
        user_id="usr_pantry_test",
        pantry_items=["paneer", "spinach", "cooked rice", "curd"],
        regional_preference="in_south_andhra"
    )
    res = recycle_pantry_ingredients(req)
    assert res.total_leftovers_analyzed == 4
    assert len(res.recycled_dishes) >= 2
    first_dish = res.recycled_dishes[0]
    assert first_dish.waste_saved_estimate_inr > 0
    assert len(first_dish.matching_leftovers_used) >= 1
    assert "Repurposed" in res.waste_diversion_summary


def test_cgm_blood_glucose_spike_predictor():
    """Verify glycemic load calculation and 3-step clinical food sequencing."""
    req = CGMPredictRequest(
        user_id="usr_cgm_test",
        meal_name="Hyderabadi Dum Biryani with Naan",
        carbs_g=78.0,
        protein_g=24.0,
        fiber_g=3.0,
        baseline_glucose_mg_dl=95.0
    )
    res = asyncio.run(predict_glucose_spike(req))
    assert res.glycemic_load > 30.0
    assert res.predicted_peak_glucose_mg_dl > 140.0
    assert res.spike_risk_category in ["MODERATE", "HIGH"]
    assert len(res.clinical_order_of_eating) == 3
    assert "Fiber Primer" in res.clinical_order_of_eating[0]["step"]
    assert "Carbohydrates (Last)" in res.clinical_order_of_eating[2]["step"]
