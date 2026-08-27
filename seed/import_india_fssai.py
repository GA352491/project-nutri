"""
Indian Food Composition Tables (IFCT) / ICMR-NIN & FSSAI Seeder

This script populates the Recipe and Food database with localized Indian nutritional data
using MongoDB and Beanie ODM, enabling the Compliance engine (ICMR-NIN / FSSAI rules)
and Recipe recommendation systems to operate with verified regional foods.
"""
import asyncio
import os
import sys

# Append backend shared module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/shared/src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/recipe/src")))

from nutriplan_shared.mongodb import init_mongodb
from recipe_service.models.food_item import FoodItem, Macronutrients, Micronutrients
from recipe_service.models.recipe import Recipe

IFCT_DATA = [
    {
        "name": "Moong Dal (Cooked)",
        "category": "Legumes & Pulses",
        "serving_size_g": 100.0,
        "macros": {
            "calories_kcal": 105.0,
            "protein_g": 7.0,
            "fat_g": 0.4,
            "carbs_g": 18.2,
            "fiber_g": 4.0
        },
        "micros": {
            "calcium_mg": 28.0,
            "iron_mg": 1.4,
            "vitamin_c_mg": 1.2,
            "vitamin_d_mcg": 0.0
        },
        "tags": ["pulse", "vegetarian", "high-protein", "staple", "gluten-free"]
    },
    {
        "name": "Toor Dal / Arhar Dal (Cooked)",
        "category": "Legumes & Pulses",
        "serving_size_g": 100.0,
        "macros": {
            "calories_kcal": 120.0,
            "protein_g": 7.8,
            "fat_g": 0.6,
            "carbs_g": 20.5,
            "fiber_g": 3.8
        },
        "micros": {
            "calcium_mg": 32.0,
            "iron_mg": 1.6,
            "vitamin_c_mg": 0.0,
            "vitamin_d_mcg": 0.0
        },
        "tags": ["pulse", "vegetarian", "staple", "gluten-free"]
    },
    {
        "name": "Paneer (Fresh Cow Milk)",
        "category": "Dairy Products",
        "serving_size_g": 100.0,
        "macros": {
            "calories_kcal": 289.0,
            "protein_g": 18.3,
            "fat_g": 22.0,
            "carbs_g": 3.4,
            "fiber_g": 0.0
        },
        "micros": {
            "calcium_mg": 480.0,
            "iron_mg": 0.2,
            "vitamin_c_mg": 0.0,
            "vitamin_d_mcg": 0.5
        },
        "tags": ["dairy", "vegetarian", "keto-friendly", "high-protein"]
    },
    {
        "name": "Whole Wheat Atta Roti",
        "category": "Cereals & Grains",
        "serving_size_g": 40.0,
        "macros": {
            "calories_kcal": 104.0,
            "protein_g": 3.2,
            "fat_g": 0.8,
            "carbs_g": 21.0,
            "fiber_g": 2.8
        },
        "micros": {
            "calcium_mg": 12.0,
            "iron_mg": 1.1,
            "vitamin_c_mg": 0.0,
            "vitamin_d_mcg": 0.0
        },
        "tags": ["grain", "staple", "vegan", "whole-grain"]
    },
    {
        "name": "Brown Basmati Rice (Cooked)",
        "category": "Cereals & Grains",
        "serving_size_g": 100.0,
        "macros": {
            "calories_kcal": 111.0,
            "protein_g": 2.6,
            "fat_g": 0.9,
            "carbs_g": 23.0,
            "fiber_g": 1.8
        },
        "micros": {
            "calcium_mg": 10.0,
            "iron_mg": 0.8,
            "vitamin_c_mg": 0.0,
            "vitamin_d_mcg": 0.0
        },
        "tags": ["grain", "vegan", "gluten-free", "low-gi"]
    },
    {
        "name": "Palak / Spinach (Raw)",
        "category": "Green Leafy Vegetables",
        "serving_size_g": 100.0,
        "macros": {
            "calories_kcal": 23.0,
            "protein_g": 2.9,
            "fat_g": 0.4,
            "carbs_g": 3.6,
            "fiber_g": 2.2
        },
        "micros": {
            "calcium_mg": 99.0,
            "iron_mg": 2.7,
            "vitamin_c_mg": 28.0,
            "vitamin_d_mcg": 0.0
        },
        "tags": ["vegetable", "green-leafy", "iron-rich", "vegan", "keto-friendly"]
    },
    {
        "name": "Idli (Steamed Fermented)",
        "category": "Fermented Foods",
        "serving_size_g": 100.0,
        "macros": {
            "calories_kcal": 132.0,
            "protein_g": 4.5,
            "fat_g": 0.8,
            "carbs_g": 26.5,
            "fiber_g": 1.2
        },
        "micros": {
            "calcium_mg": 22.0,
            "iron_mg": 0.9,
            "vitamin_c_mg": 0.0,
            "vitamin_d_mcg": 0.0
        },
        "tags": ["breakfast", "fermented", "gut-friendly", "vegan", "south-indian"]
    }
]

async def seed_database():
    print("==================================================")
    print("🇮🇳 Starting IFCT/ICMR-NIN Indian Food DB Ingestion")
    print("==================================================")

    try:
        await init_mongodb(document_models=[FoodItem, Recipe])
        print("Connected to MongoDB via Beanie ODM.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Ensure local MongoDB is running at mongodb://localhost:27017")
        return

    inserted_count = 0
    for data in IFCT_DATA:
        existing = await FoodItem.find_one(FoodItem.name == data["name"])
        if not existing:
            item = FoodItem(
                name=data["name"],
                source="IFCT",
                category=data["category"],
                serving_size_g=data["serving_size_g"],
                macros=Macronutrients(**data["macros"]),
                micros=Micronutrients(**data["micros"]),
                tags=data["tags"]
            )
            await item.insert()
            print(f"  ✓ [INSERTED] {data['name']} ({data['category']})")
            inserted_count += 1
        else:
            print(f"  • [EXISTS]   {data['name']}")

    print("--------------------------------------------------")
    print(f"✅ Seeding Complete! {inserted_count} new Indian Food items inserted.")
    print("The Recipe & Compliance Services now have active IFCT/NIN nutrition profiles.")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(seed_database())
