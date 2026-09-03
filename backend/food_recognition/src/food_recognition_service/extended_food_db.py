"""
Extended Scientific & Cafe Food Composition Database grounded in ICMR-NIN (IFCT) & USDA.
Covers home-cooked, street food, restaurant dishes, bakery items, beverages, and cafe staples.
"""
from typing import Dict
from .schemas import FoodItem

# Comprehensive open-world food dictionary
EXTENDED_FOOD_DB: Dict[str, FoodItem] = {
    # ── South Indian Regional & Cafe ──
    "pesarattu": FoodItem(name="Pesarattu (Moong Dal Crepe)", confidence=0.96, portion_g=140, calories=240, protein_g=14.5, carbs_g=34.0, fat_g=4.2, fiber_g=6.8, region="South Indian (Andhra)", is_indian_cuisine=True, fssai_code="FSSAI-06.1"),
    "ragi": FoodItem(name="Ragi Mudda / Sankati", confidence=0.94, portion_g=180, calories=220, protein_g=6.2, carbs_g=45.0, fat_g=1.2, fiber_g=8.4, region="South Indian (Rayalaseema)", is_indian_cuisine=True, fssai_code="FSSAI-06.1"),
    "idli": FoodItem(name="Steamed Idli (2 pcs) with Chutney", confidence=0.98, portion_g=120, calories=156, protein_g=5.2, carbs_g=30.0, fat_g=1.8, fiber_g=2.2, region="South Indian", is_indian_cuisine=True, fssai_code="FSSAI-06.1"),
    "dosa": FoodItem(name="Crisp Masala Dosa", confidence=0.95, portion_g=180, calories=320, protein_g=7.5, carbs_g=48.0, fat_g=11.5, fiber_g=3.2, region="South Indian", is_indian_cuisine=True, fssai_code="FSSAI-06.1"),
    "mysore masala dosa": FoodItem(name="Mysore Masala Dosa with Red Garlic Chutney", confidence=0.94, portion_g=200, calories=380, protein_g=8.2, carbs_g=52.0, fat_g=15.5, fiber_g=3.8, region="South Indian (Karnataka)", is_indian_cuisine=True),
    "medu vada": FoodItem(name="Crispy Medu Vada (2 pcs)", confidence=0.95, portion_g=100, calories=285, protein_g=7.8, carbs_g=28.0, fat_g=16.0, fiber_g=4.5, region="South Indian", is_indian_cuisine=True),
    "sambar": FoodItem(name="Drumstick & Keerai Sambar", confidence=0.93, portion_g=200, calories=110, protein_g=5.5, carbs_g=18.0, fat_g=1.8, fiber_g=4.2, region="South Indian", is_indian_cuisine=True, fssai_code="FSSAI-04.2"),
    "sundal": FoodItem(name="Black Chana Sundal", confidence=0.92, portion_g=100, calories=165, protein_g=8.9, carbs_g=23.0, fat_g=4.2, fiber_g=7.1, region="South Indian", is_indian_cuisine=True),
    "appam": FoodItem(name="Lacy Kerala Appam with Stew", confidence=0.95, portion_g=160, calories=240, protein_g=4.8, carbs_g=42.0, fat_g=6.2, fiber_g=2.8, region="South Indian (Kerala)", is_indian_cuisine=True),
    "kadala": FoodItem(name="Malabar Kadala Curry", confidence=0.94, portion_g=180, calories=220, protein_g=12.5, carbs_g=32.0, fat_g=5.2, fiber_g=8.5, region="South Indian (Kerala)", is_indian_cuisine=True),
    "bisi bele bath": FoodItem(name="Bisi Bele Bath with Boondi", confidence=0.94, portion_g=250, calories=340, protein_g=12.5, carbs_g=54.0, fat_g=8.5, fiber_g=7.5, region="South Indian (Karnataka)", is_indian_cuisine=True),
    "filter coffee": FoodItem(name="South Indian Filter Coffee (Full Milk)", confidence=0.96, portion_g=150, calories=115, protein_g=3.8, carbs_g=12.5, fat_g=4.5, fiber_g=0.0, region="South Indian", is_indian_cuisine=True),

    # ── North Indian & Restaurant Staples ──
    "butter chicken": FoodItem(name="Restaurant Butter Chicken (Murgh Makhani)", confidence=0.95, portion_g=250, calories=480, protein_g=34.0, carbs_g=12.0, fat_g=32.0, fiber_g=1.5, region="North Indian", is_indian_cuisine=True),
    "paneer": FoodItem(name="Paneer Bhurji (Low-Oil)", confidence=0.95, portion_g=150, calories=260, protein_g=19.5, carbs_g=4.5, fat_g=18.0, fiber_g=1.2, region="North Indian (Punjab)", is_indian_cuisine=True),
    "paneer butter masala": FoodItem(name="Paneer Butter Masala (Rich Cream Gravy)", confidence=0.95, portion_g=220, calories=420, protein_g=16.5, carbs_g=14.0, fat_g=34.0, fiber_g=2.2, region="North Indian", is_indian_cuisine=True),
    "paneer tikka": FoodItem(name="Tandoori Paneer Tikka (4 pcs)", confidence=0.96, portion_g=180, calories=290, protein_g=21.0, carbs_g=8.5, fat_g=19.0, fiber_g=2.5, region="North Indian", is_indian_cuisine=True),
    "dal makhani": FoodItem(name="Slow-Cooked Restaurant Dal Makhani", confidence=0.94, portion_g=220, calories=340, protein_g=14.2, carbs_g=36.0, fat_g=16.0, fiber_g=8.5, region="North Indian (Punjab)", is_indian_cuisine=True),
    "dal tadka": FoodItem(name="Yellow Moong Dal Tadka (Dhaba Style)", confidence=0.95, portion_g=200, calories=180, protein_g=10.5, carbs_g=24.0, fat_g=5.5, fiber_g=4.2, region="Pan India", is_indian_cuisine=True),
    "dal": FoodItem(name="Yellow Moong Dal Tadka", confidence=0.95, portion_g=200, calories=140, protein_g=9.5, carbs_g=20.0, fat_g=2.5, fiber_g=3.8, region="Pan India", is_indian_cuisine=True),
    "naan": FoodItem(name="Butter Garlic Naan (1 pc)", confidence=0.96, portion_g=90, calories=290, protein_g=7.5, carbs_g=46.0, fat_g=9.0, fiber_g=2.0, region="North Indian", is_indian_cuisine=True),
    "roti": FoodItem(name="Tandoori Whole Wheat Roti (2 pcs)", confidence=0.97, portion_g=80, calories=210, protein_g=6.8, carbs_g=42.0, fat_g=1.8, fiber_g=4.8, region="North Indian", is_indian_cuisine=True),
    "chole bhature": FoodItem(name="Amritsari Chole with 2 Bhature", confidence=0.96, portion_g=350, calories=680, protein_g=18.5, carbs_g=82.0, fat_g=32.0, fiber_g=9.5, region="North Indian (Punjab)", is_indian_cuisine=True),
    "rajma": FoodItem(name="Jammu Rajma Masala", confidence=0.94, portion_g=220, calories=245, protein_g=13.2, carbs_g=38.0, fat_g=4.5, fiber_g=9.5, region="North Indian (Jammu/Punjab)", is_indian_cuisine=True),
    "rajma chawal": FoodItem(name="Punjabi Rajma Masala with Steamed Rice", confidence=0.95, portion_g=350, calories=460, protein_g=17.5, carbs_g=78.0, fat_g=8.5, fiber_g=11.2, region="North Indian", is_indian_cuisine=True),
    "thepla": FoodItem(name="Methi Sattu Thepla", confidence=0.93, portion_g=65, calories=175, protein_g=6.2, carbs_g=26.0, fat_g=4.8, fiber_g=3.4, region="West Indian (Gujarat)", is_indian_cuisine=True),
    "fish_curry": FoodItem(name="Bengali Macher Jhol (Rohu)", confidence=0.95, portion_g=220, calories=240, protein_g=28.5, carbs_g=6.2, fat_g=11.0, fiber_g=1.8, region="East Indian (Bengal)", is_indian_cuisine=True),
    "biryani": FoodItem(name="Hyderabadi Dum Biryani (Chicken/Mutton)", confidence=0.96, portion_g=350, calories=560, protein_g=28.0, carbs_g=65.0, fat_g=21.0, fiber_g=3.5, region="Pan India", is_indian_cuisine=True),
    "veg biryani": FoodItem(name="Subz Dum Biryani with Mirchi ka Salan", confidence=0.94, portion_g=300, calories=420, protein_g=11.5, carbs_g=68.0, fat_g=12.0, fiber_g=6.2, region="Pan India", is_indian_cuisine=True),

    # ── Street Food, Snacks & Fast Food ──
    "samosa": FoodItem(name="Spiced Potato Punjabi Samosa (1 pc)", confidence=0.97, portion_g=90, calories=260, protein_g=4.2, carbs_g=31.0, fat_g=14.0, fiber_g=2.4, region="Pan India", is_indian_cuisine=True),
    "pav bhaji": FoodItem(name="Mumbai Butter Pav Bhaji (with 2 Pav)", confidence=0.95, portion_g=300, calories=520, protein_g=12.5, carbs_g=68.0, fat_g=23.0, fiber_g=7.5, region="West Indian (Maharashtra)", is_indian_cuisine=True),
    "vada pav": FoodItem(name="Mumbai Vada Pav with Garlic Chutney", confidence=0.96, portion_g=120, calories=295, protein_g=6.5, carbs_g=41.0, fat_g=12.5, fiber_g=3.8, region="West Indian (Maharashtra)", is_indian_cuisine=True),
    "pani puri": FoodItem(name="Pani Puri / Golgappe (6 pcs)", confidence=0.95, portion_g=150, calories=180, protein_g=3.5, carbs_g=32.0, fat_g=4.5, fiber_g=2.8, region="Pan India", is_indian_cuisine=True),
    "momos": FoodItem(name="Steamed Chicken/Veg Momos (6 pcs)", confidence=0.95, portion_g=160, calories=230, protein_g=14.0, carbs_g=30.0, fat_g=5.5, fiber_g=2.1, region="East / Himalayan", is_indian_cuisine=True),
    "kathi roll": FoodItem(name="Kolkata Chicken / Paneer Kathi Roll", confidence=0.94, portion_g=200, calories=440, protein_g=22.0, carbs_g=48.0, fat_g=18.0, fiber_g=3.2, region="East Indian (Bengal)", is_indian_cuisine=True),

    # ── Western Cafe, Bakery & Continental ──
    "cappuccino": FoodItem(name="Cafe Cappuccino (Whole Milk, No Sugar)", confidence=0.96, portion_g=200, calories=90, protein_g=5.0, carbs_g=7.5, fat_g=4.8, fiber_g=0.0, region="Global Cafe"),
    "latte": FoodItem(name="Cafe Latte (Whole Milk)", confidence=0.95, portion_g=240, calories=140, protein_g=7.2, carbs_g=11.0, fat_g=7.0, fiber_g=0.0, region="Global Cafe"),
    "cold coffee": FoodItem(name="Iced Cold Coffee with Vanilla Ice Cream", confidence=0.94, portion_g=300, calories=280, protein_g=6.0, carbs_g=38.0, fat_g=12.0, fiber_g=0.5, region="Global Cafe"),
    "croissant": FoodItem(name="Butter Bakery Croissant", confidence=0.96, portion_g=70, calories=280, protein_g=5.5, carbs_g=31.0, fat_g=15.0, fiber_g=1.5, region="Bakery"),
    "avocado toast": FoodItem(name="Avocado Toast on Sourdough with Poached Egg", confidence=0.95, portion_g=180, calories=340, protein_g=14.0, carbs_g=28.0, fat_g=19.5, fiber_g=7.2, region="Continental"),
    "pasta": FoodItem(name="Penne Pasta in Creamy Alfredo Sauce", confidence=0.94, portion_g=250, calories=520, protein_g=16.0, carbs_g=62.0, fat_g=24.0, fiber_g=3.5, region="Italian / Continental"),
    "pizza": FoodItem(name="Wood-Fired Margherita Pizza (2 Slices)", confidence=0.95, portion_g=200, calories=490, protein_g=20.0, carbs_g=56.0, fat_g=21.0, fiber_g=3.8, region="Italian / Fast Food"),
    "burger": FoodItem(name="Grilled Chicken / Veggie Supreme Burger", confidence=0.95, portion_g=220, calories=460, protein_g=24.0, carbs_g=48.0, fat_g=19.0, fiber_g=4.2, region="Fast Food"),
    "french fries": FoodItem(name="Crispy French Fries (Medium Basket)", confidence=0.97, portion_g=120, calories=365, protein_g=4.0, carbs_g=48.0, fat_g=18.0, fiber_g=4.0, region="Fast Food"),
    "caesar salad": FoodItem(name="Caesar Salad with Grilled Chicken & Croutons", confidence=0.94, portion_g=220, calories=320, protein_g=28.0, carbs_g=12.0, fat_g=18.0, fiber_g=3.5, region="Continental"),
    "cheesecake": FoodItem(name="New York Baked Cheesecake (1 slice)", confidence=0.95, portion_g=120, calories=410, protein_g=7.0, carbs_g=34.0, fat_g=28.0, fiber_g=0.5, region="Bakery / Dessert"),
    "brownie": FoodItem(name="Warm Chocolate Walnut Brownie", confidence=0.96, portion_g=80, calories=330, protein_g=4.5, carbs_g=42.0, fat_g=17.0, fiber_g=2.2, region="Bakery / Dessert"),
}
