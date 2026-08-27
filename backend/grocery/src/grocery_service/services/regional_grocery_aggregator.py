"""
Regional Grocery Aggregator Service.

Bridges the Regional Meal Plan Engine → Grocery List.
- Extracts raw ingredients from all meals in a regional plan
- Aggregates across duplicate ingredients (quantities summed)
- Categorizes by aisle/vendor: local market, wet section, dry provisions, etc.
- Persists to the Grocery DB so users see them immediately in the app
"""
from __future__ import annotations
from typing import List, Dict, Optional, Any
import uuid


# ── Category taxonomy grounded in Indian supermarkets and local mandis ──────
INGREDIENT_CATEGORY_MAP: Dict[str, str] = {
    # Grains & Millets (Dry Aisles)
    "rice": "🌾 Grains & Millets", "brown rice": "🌾 Grains & Millets", "jowar": "🌾 Grains & Millets",
    "ragi": "🌾 Grains & Millets", "bajra": "🌾 Grains & Millets", "oats": "🌾 Grains & Millets",
    "quinoa": "🌾 Grains & Millets", "wheat flour": "🌾 Grains & Millets", "besan": "🌾 Grains & Millets",
    "sooji": "🌾 Grains & Millets", "sattu": "🌾 Grains & Millets", "poha": "🌾 Grains & Millets",

    # Lentils & Legumes (Protein Section)
    "moong dal": "🫘 Dals & Legumes", "toor dal": "🫘 Dals & Legumes", "chana dal": "🫘 Dals & Legumes",
    "masoor dal": "🫘 Dals & Legumes", "urad dal": "🫘 Dals & Legumes", "rajma": "🫘 Dals & Legumes",
    "chole": "🫘 Dals & Legumes", "matki": "🫘 Dals & Legumes", "chana": "🫘 Dals & Legumes",
    "lobia": "🫘 Dals & Legumes", "moong": "🫘 Dals & Legumes", "kabuli chana": "🫘 Dals & Legumes",

    # Dairy (Refrigerated)
    "paneer": "🧀 Dairy & Eggs", "curd": "🧀 Dairy & Eggs", "ghee": "🧀 Dairy & Eggs",
    "milk": "🧀 Dairy & Eggs", "buttermilk": "🧀 Dairy & Eggs", "egg": "🧀 Dairy & Eggs",
    "eggs": "🧀 Dairy & Eggs", "cheese": "🧀 Dairy & Eggs", "yogurt": "🧀 Dairy & Eggs",

    # Fresh Vegetables (Wet Mandis)
    "spinach": "🥦 Fresh Vegetables", "palak": "🥦 Fresh Vegetables", "methi": "🥦 Fresh Vegetables",
    "drumstick": "🥦 Fresh Vegetables", "karela": "🥦 Fresh Vegetables", "bottle gourd": "🥦 Fresh Vegetables",
    "bitter gourd": "🥦 Fresh Vegetables", "tomato": "🥦 Fresh Vegetables", "onion": "🥦 Fresh Vegetables",
    "capsicum": "🥦 Fresh Vegetables", "brinjal": "🥦 Fresh Vegetables", "cauliflower": "🥦 Fresh Vegetables",
    "beans": "🥦 Fresh Vegetables", "peas": "🥦 Fresh Vegetables", "potato": "🥦 Fresh Vegetables",
    "cucumber": "🥦 Fresh Vegetables", "radish": "🥦 Fresh Vegetables", "cabbage": "🥦 Fresh Vegetables",
    "carrot": "🥦 Fresh Vegetables", "kale": "🥦 Fresh Vegetables",

    # Fresh Fruits
    "banana": "🍎 Fresh Fruits", "apple": "🍎 Fresh Fruits", "papaya": "🍎 Fresh Fruits",
    "guava": "🍎 Fresh Fruits", "mango": "🍎 Fresh Fruits", "orange": "🍎 Fresh Fruits",
    "pomegranate": "🍎 Fresh Fruits", "amla": "🍎 Fresh Fruits",

    # Proteins (Non-Veg Wet Section)
    "chicken": "🍗 Proteins (Non-Veg)", "fish": "🍗 Proteins (Non-Veg)", "rohu": "🍗 Proteins (Non-Veg)",
    "katla": "🍗 Proteins (Non-Veg)", "mutton": "🍗 Proteins (Non-Veg)", "prawn": "🍗 Proteins (Non-Veg)",

    # Spices & Condiments
    "turmeric": "🌶️ Spices & Condiments", "coriander": "🌶️ Spices & Condiments", "cumin": "🌶️ Spices & Condiments",
    "mustard seeds": "🌶️ Spices & Condiments", "curry leaves": "🌶️ Spices & Condiments",
    "green chilli": "🌶️ Spices & Condiments", "ginger": "🌶️ Spices & Condiments",
    "garlic": "🌶️ Spices & Condiments", "asafoetida": "🌶️ Spices & Condiments",
    "fenugreek": "🌶️ Spices & Condiments", "tamarind": "🌶️ Spices & Condiments",
    "red chilli": "🌶️ Spices & Condiments", "garam masala": "🌶️ Spices & Condiments",
    "salt": "🌶️ Spices & Condiments", "pepper": "🌶️ Spices & Condiments",

    # Oils & Fats
    "sunflower oil": "🫙 Oils & Fats", "coconut oil": "🫙 Oils & Fats", "groundnut oil": "🫙 Oils & Fats",
    "mustard oil": "🫙 Oils & Fats", "sesame oil": "🫙 Oils & Fats", "olive oil": "🫙 Oils & Fats",

    # Superfoods & Supplements
    "makhana": "💊 Superfoods & Nuts", "almonds": "💊 Superfoods & Nuts", "walnuts": "💊 Superfoods & Nuts",
    "flaxseed": "💊 Superfoods & Nuts", "chia seeds": "💊 Superfoods & Nuts",
    "pumpkin seeds": "💊 Superfoods & Nuts", "sunflower seeds": "💊 Superfoods & Nuts",
    "coconut": "💊 Superfoods & Nuts", "peanuts": "💊 Superfoods & Nuts",
}

DEFAULT_CATEGORY = "🛒 General"


def classify_ingredient(name: str) -> str:
    """Fuzzy category lookup — matches the ingredient name against our taxonomy."""
    lowered = name.lower().strip()
    # Exact match
    if lowered in INGREDIENT_CATEGORY_MAP:
        return INGREDIENT_CATEGORY_MAP[lowered]
    # Partial match — iterate and pick best match
    for key, cat in INGREDIENT_CATEGORY_MAP.items():
        if key in lowered or lowered in key:
            return cat
    return DEFAULT_CATEGORY


def aggregate_ingredients_from_plan(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Given a regional meal plan dict (from RegionalOptimizer output),
    extracts and aggregates all ingredients across meals.
    
    Returns a list of dicts ready to insert into GroceryItem.
    """
    ingredient_totals: Dict[str, Dict[str, Any]] = {}

    for meal in plan.get("meals", []):
        ingredients = meal.get("ingredients", [])
        for ing in ingredients:
            raw_name = ing.get("name", "").strip()
            if not raw_name:
                continue
            key = raw_name.lower()
            qty = float(ing.get("quantity_g", 0))
            unit = ing.get("unit", "g")

            if key in ingredient_totals:
                ingredient_totals[key]["quantity"] += qty
            else:
                ingredient_totals[key] = {
                    "id": str(uuid.uuid4()),
                    "name": raw_name,
                    "quantity": qty,
                    "unit": unit,
                    "category": classify_ingredient(raw_name),
                    "source_meals": [],
                    "is_checked": False,
                }

            # Track which meal it comes from
            ingredient_totals[key]["source_meals"].append(meal.get("name", ""))

    # Sort by category, then name
    result = sorted(ingredient_totals.values(), key=lambda x: (x["category"], x["name"]))
    return result


def group_by_category(
    flat_ingredients: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """Group aggregated ingredients by their aisle/vendor category."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for ing in flat_ingredients:
        cat = ing["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(ing)
    return grouped
