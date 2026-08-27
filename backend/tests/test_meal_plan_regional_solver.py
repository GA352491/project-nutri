import pytest
import sys
import os

sys.path.extend([
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../shared/src")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../meal_plan/src")),
])

from meal_plan_service.services.regional_optimizer import RegionalOptimizer

def test_regional_optimizer_single_region():
    """Verify solve_daily_plan produces 4 distinct meals matching target calories within tolerance."""
    optimizer = RegionalOptimizer()
    plan = optimizer.solve_daily_plan(
        region_id="in_south_andhra",
        caloric_target=2000,
        dietary_flag="vegetarian",
        day_seed=1
    )
    assert len(plan["meals"]) == 4
    meal_types = [m["meal_type"] for m in plan["meals"]]
    assert set(meal_types) == {"breakfast", "lunch", "snack", "dinner"}
    assert abs(plan["total_calories"] - 2000) <= 300
    assert plan["total_protein_g"] > 30

def test_regional_optimizer_7day_variety():
    """Verify that different day_seeds produce distinct recipe titles across days."""
    optimizer = RegionalOptimizer()
    day1 = optimizer.solve_daily_plan(region_id="in_north_punjab", caloric_target=1800, day_seed=1)
    day2 = optimizer.solve_daily_plan(region_id="in_north_punjab", caloric_target=1800, day_seed=2)
    day3 = optimizer.solve_daily_plan(region_id="in_north_punjab", caloric_target=1800, day_seed=3)

    titles1 = [m["name"] for m in day1["meals"]]
    titles2 = [m["name"] for m in day2["meals"]]
    titles3 = [m["name"] for m in day3["meals"]]

    # Ensure not identical across days
    assert titles1 != titles2
    assert titles2 != titles3

def test_regional_optimizer_fallback_unknown_region():
    """Verify that unknown region gracefully falls back to catalog pool without error."""
    optimizer = RegionalOptimizer()
    plan = optimizer.solve_daily_plan(
        region_id="non_existent_region_xyz",
        caloric_target=2100,
        day_seed=42
    )
    assert len(plan["meals"]) == 4
    assert plan["total_calories"] > 0
