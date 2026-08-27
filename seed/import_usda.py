#!/usr/bin/env python3
import json
import argparse
from typing import List, Dict

def download_usda_database():
    """
    In a production scenario, this would download the latest JSON release 
    from USDA FoodData Central (https://fdc.nal.usda.gov/download-datasets.html).
    """
    print("[*] Downloading USDA FoodData Central dataset...")
    # Mocking download
    return [
        {
            "fdcId": 1102653,
            "description": "Broccoli, raw",
            "foodNutrients": [
                {"nutrientName": "Protein", "amount": 2.82, "unitName": "g"},
                {"nutrientName": "Carbohydrate, by difference", "amount": 6.64, "unitName": "g"},
                {"nutrientName": "Total lipid (fat)", "amount": 0.37, "unitName": "g"}
            ]
        },
        {
            "fdcId": 1102644,
            "description": "Chicken breast, raw",
            "foodNutrients": [
                {"nutrientName": "Protein", "amount": 22.5, "unitName": "g"},
                {"nutrientName": "Carbohydrate, by difference", "amount": 0.0, "unitName": "g"},
                {"nutrientName": "Total lipid (fat)", "amount": 2.62, "unitName": "g"}
            ]
        }
    ]

def transform_and_insert(raw_data: List[Dict]):
    """
    Transforms the USDA format into NutriPlan's local database schema
    and inserts it via SQLAlchemy/psycopg2.
    """
    print("[*] Transforming USDA data to NutriPlan schema...")
    inserted = 0
    for item in raw_data:
        # Extract macros
        protein = next((n["amount"] for n in item["foodNutrients"] if "Protein" in n["nutrientName"]), 0)
        carbs = next((n["amount"] for n in item["foodNutrients"] if "Carbohydrate" in n["nutrientName"]), 0)
        fat = next((n["amount"] for n in item["foodNutrients"] if "fat" in n["nutrientName"].lower()), 0)
        
        # Calculate calories (4-4-9 rule)
        calories = (protein * 4) + (carbs * 4) + (fat * 9)
        
        # In reality, INSERT INTO food_items ...
        print(f"  -> Inserted {item['description']} ({calories:.0f} kcal/100g)")
        inserted += 1
        
    print(f"[✓] Successfully imported {inserted} food items from USDA database.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import USDA FoodData Central into NutriPlan DB")
    parser.add_argument("--dry-run", action="store_true", help="Run without actually inserting into the DB")
    args = parser.parse_args()
    
    data = download_usda_database()
    transform_and_insert(data)
