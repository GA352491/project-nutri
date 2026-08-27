#!/usr/bin/env python3
"""
USDA FoodData Central — Import Script
=====================================

Downloads structured food data from the USDA FoodData Central API and seeds
it into the NutriPlan recipe service's MongoDB instance.

API: https://api.nal.usda.gov/fdc/v1/
Docs: https://fdc.nal.usda.gov/api-guide.html

Usage:
    # Set environment variables first
    export MONGO_URI="mongodb://localhost:27017"
    export MONGO_DB="nutriplan_recipes"
    export USDA_API_KEY="DEMO_KEY"   # register for free at https://api.nal.usda.gov/

    python scripts/import_usda.py [--limit 500] [--data-type Foundation SR\ Legacy]

Requirements:
    pip install httpx motor tqdm python-dotenv
"""
import asyncio
import argparse
import os
import sys
from datetime import datetime
from typing import Optional

try:
    import httpx
    import motor.motor_asyncio
    from tqdm import tqdm
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install httpx motor tqdm python-dotenv")
    sys.exit(1)

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "nutriplan_recipes")
COLLECTION = "food_items"

# Nutrients we care about (USDA nutrient IDs → our field names)
NUTRIENT_MAP = {
    1003: "protein_g",
    1004: "fat_g",
    1005: "carbs_g",
    1008: "calories_kcal",
    1079: "fiber_g",
    2000: "sugar_g",
    1093: "sodium_mg",
    1087: "calcium_mg",
    1089: "iron_mg",
    1092: "potassium_mg",
    1114: "vitamin_d_mcg",
    1109: "vitamin_e_mg",
    1162: "vitamin_c_mg",
    1175: "vitamin_b6_mg",
    1178: "vitamin_b12_mcg",
    1190: "folate_mcg",
    1091: "phosphorus_mg",
    1095: "zinc_mg",
}


async def fetch_food_list(
    client: httpx.AsyncClient,
    data_types: list[str],
    page_size: int = 200,
    page: int = 1,
) -> dict:
    """Fetch a page of foods from USDA FoodData Central search."""
    payload = {
        "dataType": data_types,
        "pageSize": page_size,
        "pageNumber": page,
        "sortBy": "dataType.keyword",
        "sortOrder": "asc",
    }
    resp = await client.post(
        f"{USDA_BASE_URL}/foods/list",
        params={"api_key": USDA_API_KEY},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def extract_nutrients(food_item: dict) -> dict:
    """Extract only the nutrients we track from a USDA food item."""
    nutrients = {}
    for n in food_item.get("foodNutrients", []):
        nutrient_id = n.get("nutrientId") or (n.get("nutrient", {}).get("id"))
        amount = n.get("value") or n.get("amount") or 0.0
        if nutrient_id in NUTRIENT_MAP:
            nutrients[NUTRIENT_MAP[nutrient_id]] = round(float(amount), 2)
    return nutrients


def transform_food(food_item: dict) -> Optional[dict]:
    """Transform a USDA food item into NutriPlan FoodItem format."""
    name = food_item.get("description", "").strip()
    if not name:
        return None

    nutrients = extract_nutrients(food_item)

    return {
        "_source": "usda_fdc",
        "fdc_id": food_item.get("fdcId"),
        "name": name,
        "data_type": food_item.get("dataType", ""),
        "food_category": food_item.get("foodCategory", ""),
        "brand_owner": food_item.get("brandOwner", ""),
        # Per 100g serving as USDA reports
        "serving_size_g": 100,
        "calories_kcal": nutrients.get("calories_kcal", 0.0),
        "protein_g":     nutrients.get("protein_g", 0.0),
        "carbs_g":       nutrients.get("carbs_g", 0.0),
        "fat_g":         nutrients.get("fat_g", 0.0),
        "fiber_g":       nutrients.get("fiber_g", 0.0),
        "sugar_g":       nutrients.get("sugar_g", 0.0),
        "sodium_mg":     nutrients.get("sodium_mg", 0.0),
        "potassium_mg":  nutrients.get("potassium_mg", 0.0),
        "calcium_mg":    nutrients.get("calcium_mg", 0.0),
        "iron_mg":       nutrients.get("iron_mg", 0.0),
        "zinc_mg":       nutrients.get("zinc_mg", 0.0),
        "vitamin_d_mcg": nutrients.get("vitamin_d_mcg", 0.0),
        "vitamin_c_mg":  nutrients.get("vitamin_c_mg", 0.0),
        "vitamin_b12_mcg": nutrients.get("vitamin_b12_mcg", 0.0),
        "folate_mcg":    nutrients.get("folate_mcg", 0.0),
        "phosphorus_mg": nutrients.get("phosphorus_mg", 0.0),
        "is_verified": True,
        "country": "US",
        "imported_at": datetime.utcnow().isoformat(),
    }


async def run_import(limit: int, data_types: list[str]):
    print(f"\n🌾 USDA FoodData Central Import")
    print(f"   Data types  : {', '.join(data_types)}")
    print(f"   Limit       : {limit} foods")
    print(f"   USDA key    : {USDA_API_KEY[:8]}...")
    print(f"   Mongo URI   : {MONGO_URI}\n")

    # Connect to MongoDB
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    collection = db[COLLECTION]

    # Create index on fdc_id to avoid duplicates
    await collection.create_index("fdc_id", unique=True)

    inserted = 0
    skipped = 0
    errors = 0
    page = 1
    page_size = min(200, limit)

    async with httpx.AsyncClient() as client:
        with tqdm(total=limit, desc="Importing", unit="foods") as pbar:
            while inserted + skipped < limit:
                try:
                    data = await fetch_food_list(client, data_types, page_size=page_size, page=page)
                except httpx.HTTPError as e:
                    print(f"\n⚠️  HTTP error on page {page}: {e}")
                    errors += 1
                    if errors > 3:
                        break
                    await asyncio.sleep(2)
                    continue

                if not data:
                    break

                foods = data if isinstance(data, list) else data.get("foods", [])
                if not foods:
                    break

                docs = []
                for food in foods:
                    doc = transform_food(food)
                    if doc:
                        docs.append(doc)

                if not docs:
                    page += 1
                    continue

                # Bulk upsert by fdc_id
                from pymongo import UpdateOne
                ops = [
                    UpdateOne(
                        {"fdc_id": doc["fdc_id"]},
                        {"$setOnInsert": doc},
                        upsert=True
                    )
                    for doc in docs
                ]
                try:
                    result = await collection.bulk_write(ops, ordered=False)
                    batch_inserted = result.upserted_count
                    batch_skipped = len(docs) - batch_inserted
                    inserted += batch_inserted
                    skipped += batch_skipped
                    pbar.update(len(docs))
                except Exception as e:
                    print(f"\n⚠️  Mongo write error: {e}")
                    errors += 1

                page += 1
                remaining = limit - (inserted + skipped)
                if remaining <= 0:
                    break
                page_size = min(200, remaining)

    print(f"\n✅ Import complete!")
    print(f"   Inserted : {inserted}")
    print(f"   Skipped  : {skipped} (already existed)")
    print(f"   Errors   : {errors}")
    mongo_client.close()


def main():
    parser = argparse.ArgumentParser(
        description="Import USDA FoodData Central into NutriPlan MongoDB"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Maximum number of food items to import (default: 500)",
    )
    parser.add_argument(
        "--data-type",
        nargs="+",
        default=["Foundation", "SR Legacy"],
        dest="data_types",
        help="USDA data types to include (default: Foundation SR Legacy)",
    )
    args = parser.parse_args()

    asyncio.run(run_import(limit=args.limit, data_types=args.data_types))


if __name__ == "__main__":
    main()
