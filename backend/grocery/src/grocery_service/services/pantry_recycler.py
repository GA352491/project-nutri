"""
Pantry Zero-Waste & Leftover Recycler.

Takes remaining items in user's fridge/pantry (e.g. paneer, tomatoes, spinach, cooked rice, curd)
and synthesizes quick Indian regional recipes and meal slots to prevent food waste.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class PantryLeftoverRequest(BaseModel):
    user_id: str
    pantry_items: List[str] = ["paneer", "spinach", "cooked rice", "tomatoes"]
    regional_preference: str = "in_south_andhra"
    target_meal: Optional[str] = "dinner"  # 'lunch' | 'dinner' | 'snack'


class RecycledDish(BaseModel):
    dish_name: str
    matching_leftovers_used: List[str]
    missing_pantry_staples: List[str]
    prep_time_mins: int
    estimated_calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    waste_saved_estimate_inr: int
    cooking_tip: str


class PantryRecyclerResponse(BaseModel):
    user_id: str
    total_leftovers_analyzed: int
    recycled_dishes: List[RecycledDish]
    waste_diversion_summary: str


PANTRY_RECIPES_CATALOG = [
    {
        "name": "Palak Paneer Bhurji with Roti",
        "keywords": ["paneer", "spinach", "palak", "onion", "tomato"],
        "prep_mins": 15,
        "cal": 320, "p": 20.0, "c": 18.0, "f": 19.0,
        "savings_inr": 120,
        "tip": "Sauté leftover spinach with crumbled paneer and roasted cumin for a 15-min high-protein dinner."
    },
    {
        "name": "Tomato Curd Rice Tadka (South Indian Comfort)",
        "keywords": ["cooked rice", "rice", "curd", "yogurt", "tomato", "mustard"],
        "prep_mins": 10,
        "cal": 280, "p": 8.5, "c": 44.0, "f": 7.0,
        "savings_inr": 60,
        "tip": "Mix cooked rice with fresh curd, add ginger-curry leaf tempering, and top with diced tomatoes."
    },
    {
        "name": "Spiced Leftover Dal Tadka Khichdi",
        "keywords": ["dal", "lentil", "rice", "cooked rice", "ghee"],
        "prep_mins": 12,
        "cal": 310, "p": 12.0, "c": 52.0, "f": 6.5,
        "savings_inr": 75,
        "tip": "Combine leftover yellow dal with cold rice, simmer with hing and jeera for a comforting digestive meal."
    },
    {
        "name": "Paneer & Capsicum Masala Wrap",
        "keywords": ["paneer", "capsicum", "bell pepper", "roti", "onion"],
        "prep_mins": 15,
        "cal": 360, "p": 22.0, "c": 32.0, "f": 16.0,
        "savings_inr": 110,
        "tip": "Toss paneer cubes and capsicum on high heat with chat masala and roll into a warm roti."
    },
    {
        "name": "Vegetable Egg / Soya Scramble",
        "keywords": ["egg", "soya", "onion", "tomato", "green chili"],
        "prep_mins": 10,
        "cal": 250, "p": 19.0, "c": 10.0, "f": 14.0,
        "savings_inr": 50,
        "tip": "Quick skillet scramble incorporating remaining herbs and diced onions."
    }
]


def recycle_pantry_ingredients(req: PantryLeftoverRequest) -> PantryRecyclerResponse:
    cleaned_input = [item.strip().lower() for item in req.pantry_items]
    matched: List[RecycledDish] = []

    for recipe in PANTRY_RECIPES_CATALOG:
        used = [kw for kw in recipe["keywords"] if any(kw in item for item in cleaned_input)]
        if len(used) >= 1:
            missing = [kw for kw in recipe["keywords"] if kw not in used][:2]
            matched.append(RecycledDish(
                dish_name=recipe["name"],
                matching_leftovers_used=used,
                missing_pantry_staples=missing,
                prep_time_mins=recipe["prep_mins"],
                estimated_calories=recipe["cal"],
                protein_g=recipe["p"],
                carbs_g=recipe["c"],
                fat_g=recipe["f"],
                waste_saved_estimate_inr=recipe["savings_inr"],
                cooking_tip=recipe["tip"]
            ))

    # Sort by highest ingredient match count
    matched.sort(key=lambda x: len(x.matching_leftovers_used), reverse=True)
    top_dishes = matched[:3] if matched else [
        RecycledDish(
            dish_name="Quick Masala Vegetable Stir-fry",
            matching_leftovers_used=cleaned_input[:2],
            missing_pantry_staples=["mustard seeds", "turmeric"],
            prep_time_mins=12,
            estimated_calories=220,
            protein_g=8.0,
            carbs_g=24.0,
            fat_g=9.0,
            waste_saved_estimate_inr=80,
            cooking_tip="Sauté available veggies on high flame with salt, jeera, and turmeric."
        )
    ]

    total_saved = sum(d.waste_saved_estimate_inr for d in top_dishes)
    return PantryRecyclerResponse(
        user_id=req.user_id,
        total_leftovers_analyzed=len(cleaned_input),
        recycled_dishes=top_dishes,
        waste_diversion_summary=f"Repurposed {len(cleaned_input)} fridge ingredients. Saves approx. ₹{total_saved} and prevents perishable waste."
    )
