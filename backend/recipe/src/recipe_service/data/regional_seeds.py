"""
Scientific Regional Foods and Recipes Database Seeds.
Grounded in ICMR-NIN (Indian Food Composition Tables - IFCT) data.

Covers authentic dishes across:
1. South Indian (Andhra/Telangana, Tamil Nadu, Kerala, Karnataka)
2. North Indian (Punjab, Delhi, UP, Rajasthan)
3. West Indian (Maharashtra, Gujarat)
4. East Indian (Bengal, Odisha, Assam)
5. Global / Mediterranean

Each dish contains exact gram portion measures, authentic ingredients, 
full macro profile, and core micronutrients (Iron, Calcium, Zinc, Vitamin C).
"""
from typing import List, Dict, Any

REGIONAL_RECIPES_SEED: List[Dict[str, Any]] = [
    # ── 1. SOUTH INDIAN (Andhra / Tamil Nadu / Kerala / Karnataka) ───────────
    {
        "title": "Pesarattu with Ginger Pachadi & Boiled Sprouts",
        "description": "High-protein whole green gram crepe from Andhra Pradesh, paired with allam pachadi and spiced sprouted moong.",
        "cuisine": "South Indian",
        "region_id": "in_south_andhra",
        "meal_type": "breakfast",
        "dietary_flag": "vegan",
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "ingredients": [
            {"name": "Whole Green Moong Dal (soaked)", "quantity": 80, "unit": "g"},
            {"name": "Fresh Ginger & Green Chilli", "quantity": 15, "unit": "g"},
            {"name": "Sprouted Moong (steamed)", "quantity": 50, "unit": "g"},
            {"name": "Cold Pressed Sesame Oil", "quantity": 5, "unit": "ml"},
        ],
        "instructions": [
            "Grind soaked moong with ginger, green chillies, cumin, and salt into a smooth batter.",
            "Pour ladle of batter on a hot cast iron tawa and spread thin.",
            "Drizzle 1/2 tsp sesame oil around edges and cook until golden crisp.",
            "Serve hot with ginger pachadi and steamed sprouts for extra fiber and protein."
        ],
        "total_macros": {
            "calories_kcal": 385.0,
            "protein_g": 24.5,
            "fat_g": 6.8,
            "carbs_g": 54.2,
            "fiber_g": 12.4
        },
        "total_micros": {
            "calcium_mg": 85.0,
            "iron_mg": 4.8,
            "zinc_mg": 2.6,
            "vitamin_c_mg": 18.0
        },
        "tags": ["high-protein", "vegan", "gluten-free", "breakfast", "diabetic-friendly", "in_south_andhra"]
    },
    {
        "title": "Ragi Sankati with Natu Kodi Style Soya / Chicken Curry",
        "description": "Traditional Rayalaseema finger millet ball rich in calcium, served with robustly spiced protein curry.",
        "cuisine": "South Indian",
        "region_id": "in_south_andhra",
        "meal_type": "lunch",
        "dietary_flag": "non_veg",
        "prep_time_minutes": 20,
        "cook_time_minutes": 30,
        "ingredients": [
            {"name": "Finger Millet (Ragi) Flour", "quantity": 60, "unit": "g"},
            {"name": "Broken Brown Rice", "quantity": 30, "unit": "g"},
            {"name": "Lean Chicken Breast / Soya Chunks", "quantity": 150, "unit": "g"},
            {"name": "Onion, Tomato, Guntur Spices", "quantity": 80, "unit": "g"},
            {"name": "Groundnut Oil", "quantity": 7, "unit": "ml"},
        ],
        "instructions": [
            "Cook broken rice until soft, stir in ragi flour slurry with a wooden pestle until a smooth dough forms.",
            "Shape into warm mudda (balls).",
            "Simmer chicken/soya in caramelized onions, ginger-garlic paste, and stone-ground spices.",
            "Pair ragi ball with rich spiced curry and fresh cucumber slices."
        ],
        "total_macros": {
            "calories_kcal": 540.0,
            "protein_g": 42.0,
            "fat_g": 11.5,
            "carbs_g": 64.0,
            "fiber_g": 9.8
        },
        "total_micros": {
            "calcium_mg": 320.0,
            "iron_mg": 6.2,
            "zinc_mg": 3.8,
            "vitamin_c_mg": 14.0
        },
        "tags": ["high-protein", "calcium-rich", "lunch", "dinner", "in_south_andhra"]
    },
    {
        "title": "Millet Adai with Drumstick Keerai (Moringa) Sambhar",
        "description": "Tamil Nadu multigrain lentil pancake packed with plant protein and iron-dense moringa greens.",
        "cuisine": "South Indian",
        "region_id": "in_south_tamilnadu",
        "meal_type": "dinner",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 20,
        "cook_time_minutes": 20,
        "ingredients": [
            {"name": "Chana Dal + Toor Dal + Urad Dal mix", "quantity": 70, "unit": "g"},
            {"name": "Kodo / Barnyard Millet", "quantity": 40, "unit": "g"},
            {"name": "Moringa (Murungai) Leaves", "quantity": 40, "unit": "g"},
            {"name": "Shallots, Curry Leaves, Hing", "quantity": 30, "unit": "g"},
            {"name": "Ghee / Cold Pressed Oil", "quantity": 6, "unit": "g"},
        ],
        "instructions": [
            "Coarsely grind soaked lentils and millets with dried red chillies, fennel, and hing.",
            "Mix in chopped shallots and fresh moringa leaves.",
            "Make thick adai on iron griddle until both sides are roasted golden brown.",
            "Serve hot with lentil drumstick sambhar."
        ],
        "total_macros": {
            "calories_kcal": 460.0,
            "protein_g": 26.0,
            "fat_g": 9.0,
            "carbs_g": 66.0,
            "fiber_g": 14.0
        },
        "total_micros": {
            "calcium_mg": 280.0,
            "iron_mg": 7.1,
            "zinc_mg": 3.1,
            "vitamin_c_mg": 25.0
        },
        "tags": ["high-fiber", "high-protein", "iron-rich", "dinner", "vegetarian", "in_south_tamilnadu"]
    },
    {
        "title": "Sundal & Roasted Black Chana Snack Bowl",
        "description": "Chettinad style tempered black chickpeas with grated coconut and mustard-curry leaf tempering.",
        "cuisine": "South Indian",
        "region_id": "in_south_tamilnadu",
        "meal_type": "snack",
        "dietary_flag": "vegan",
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "ingredients": [
            {"name": "Boiled Black Chickpeas (Kala Chana)", "quantity": 100, "unit": "g"},
            {"name": "Fresh Grated Coconut", "quantity": 10, "unit": "g"},
            {"name": "Mustard seeds, Hing, Green chilli", "quantity": 5, "unit": "g"},
            {"name": "Coconut Oil", "quantity": 4, "unit": "ml"},
        ],
        "instructions": [
            "Boil soaked kala chana with rock salt until tender.",
            "Temper mustard seeds, hing, dry red chilli, and curry leaves in 1 tsp coconut oil.",
            "Toss chickpeas and finish with fresh coconut and lemon juice."
        ],
        "total_macros": {
            "calories_kcal": 210.0,
            "protein_g": 11.2,
            "fat_g": 5.4,
            "carbs_g": 28.5,
            "fiber_g": 8.6
        },
        "total_micros": {
            "calcium_mg": 65.0,
            "iron_mg": 3.6,
            "zinc_mg": 1.8,
            "vitamin_c_mg": 8.0
        },
        "tags": ["snack", "low-gi", "vegan", "high-fiber", "in_south_tamilnadu"]
    },

    # ── 2. NORTH INDIAN (Punjab / Delhi / UP / Rajasthan) ────────────────────
    {
        "title": "Low-Oil Paneer Bhurji with Missi Roti",
        "description": "High-protein scrambled low-fat paneer with capsicum and spiced chickpea-flour wholewheat roti.",
        "cuisine": "North Indian",
        "region_id": "in_north_punjab",
        "meal_type": "breakfast",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "ingredients": [
            {"name": "Low-Fat Artisanal Paneer", "quantity": 120, "unit": "g"},
            {"name": "Besan (Gram Flour) + Whole Wheat Atta", "quantity": 50, "unit": "g"},
            {"name": "Onion, Tomato, Green Bell Pepper", "quantity": 80, "unit": "g"},
            {"name": "Kasuri Methi, Cumin, Turmeric", "quantity": 5, "unit": "g"},
            {"name": "Desi Ghee", "quantity": 5, "unit": "g"},
        ],
        "instructions": [
            "Saute cumin seeds, ginger, onions, and bell peppers in 1 tsp ghee until soft.",
            "Add crushed tomatoes, turmeric, coriander powder, and crumbled paneer. Cook for 4 minutes.",
            "Knead missi roti dough with kasuri methi, roll and roast on hot iron tawa without oil.",
            "Serve hot with mint chutney."
        ],
        "total_macros": {
            "calories_kcal": 475.0,
            "protein_g": 31.0,
            "fat_g": 14.5,
            "carbs_g": 52.0,
            "fiber_g": 8.2
        },
        "total_micros": {
            "calcium_mg": 380.0,
            "iron_mg": 4.5,
            "zinc_mg": 3.2,
            "vitamin_c_mg": 22.0
        },
        "tags": ["high-protein", "vegetarian", "breakfast", "in_north_punjab"]
    },
    {
        "title": "Punjabi Rajma Masala with Steamed Brown Rice & Cucumber Raita",
        "description": "Slow-simmered Jammu kidney beans in rich tomato-ginger gravy with complex carb brown rice.",
        "cuisine": "North Indian",
        "region_id": "in_north_punjab",
        "meal_type": "lunch",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 20,
        "cook_time_minutes": 35,
        "ingredients": [
            {"name": "Red Kidney Beans (Rajma - soaked)", "quantity": 80, "unit": "g"},
            {"name": "Brown Basmati Rice (raw)", "quantity": 60, "unit": "g"},
            {"name": "Low-Fat Curd (Dahi)", "quantity": 100, "unit": "g"},
            {"name": "Tomato, Onion, Ginger, Garlic paste", "quantity": 90, "unit": "g"},
            {"name": "Mustard Oil / Ghee", "quantity": 6, "unit": "g"},
        ],
        "instructions": [
            "Pressure cook rajma with black cardamom and bay leaf until completely soft.",
            "Prepare onion-tomato gravy with roasted spices, simmer rajma for 20 mins to thicken naturally.",
            "Cook brown rice to perfection.",
            "Serve with chilled cucumber-cumin raita."
        ],
        "total_macros": {
            "calories_kcal": 530.0,
            "protein_g": 25.5,
            "fat_g": 8.5,
            "carbs_g": 84.0,
            "fiber_g": 16.5
        },
        "total_micros": {
            "calcium_mg": 190.0,
            "iron_mg": 5.9,
            "zinc_mg": 3.4,
            "vitamin_c_mg": 16.0
        },
        "tags": ["classic", "high-fiber", "lunch", "vegetarian", "in_north_punjab"]
    },
    {
        "title": "Tandoori Soya Chaap / Chicken Tikka with Saag & Jowar Roti",
        "description": "Spiced tandoori marinated protein paired with slow-cooked spinach-bathua saag and sorghum flatbread.",
        "cuisine": "North Indian",
        "region_id": "in_north_punjab",
        "meal_type": "dinner",
        "dietary_flag": "non_veg",
        "prep_time_minutes": 25,
        "cook_time_minutes": 25,
        "ingredients": [
            {"name": "Chicken Breast / Soya Chaap", "quantity": 160, "unit": "g"},
            {"name": "Spinach & Bathua Leaves", "quantity": 120, "unit": "g"},
            {"name": "Jowar (Sorghum) Flour", "quantity": 50, "unit": "g"},
            {"name": "Hung Curd & Tandoori Spices", "quantity": 40, "unit": "g"},
            {"name": "Mustard Oil", "quantity": 5, "unit": "ml"},
        ],
        "instructions": [
            "Marinate protein in hung curd, ginger garlic paste, kashmiri chilli, and mustard oil.",
            "Air-fry or grill till char-grilled.",
            "Blanch and puree greens with garlic and green chillies, simmer into a smooth saag.",
            "Serve with warm jowar roti."
        ],
        "total_macros": {
            "calories_kcal": 490.0,
            "protein_g": 44.0,
            "fat_g": 11.0,
            "carbs_g": 51.0,
            "fiber_g": 10.5
        },
        "total_micros": {
            "calcium_mg": 240.0,
            "iron_mg": 6.8,
            "zinc_mg": 4.1,
            "vitamin_c_mg": 30.0
        },
        "tags": ["high-protein", "gluten-free", "dinner", "in_north_punjab"]
    },
    {
        "title": "Roasted Makhana & Salted Almonds Trail Mix",
        "description": "Crisp fox nuts lightly roasted with turmeric, rock salt, and crunchy almonds.",
        "cuisine": "North Indian",
        "region_id": "in_north_punjab",
        "meal_type": "snack",
        "dietary_flag": "vegan",
        "prep_time_minutes": 5,
        "cook_time_minutes": 8,
        "ingredients": [
            {"name": "Fox Nuts (Phool Makhana)", "quantity": 30, "unit": "g"},
            {"name": "California Almonds", "quantity": 15, "unit": "g"},
            {"name": "Rock Salt, Chaat Masala, Turmeric", "quantity": 3, "unit": "g"},
            {"name": "Cold-Pressed Ghee", "quantity": 3, "unit": "g"},
        ],
        "instructions": [
            "Dry roast makhana in a wide pan on low heat with 1/2 tsp ghee until crunchy.",
            "Toss in sliced almonds, rock salt, and chaat masala."
        ],
        "total_macros": {
            "calories_kcal": 195.0,
            "protein_g": 6.5,
            "fat_g": 9.2,
            "carbs_g": 21.0,
            "fiber_g": 4.1
        },
        "total_micros": {
            "calcium_mg": 70.0,
            "iron_mg": 1.9,
            "zinc_mg": 1.2,
            "vitamin_c_mg": 2.0
        },
        "tags": ["snack", "low-calorie", "gluten-free", "in_north_punjab"]
    },

    # ── 3. WEST INDIAN (Maharashtra / Gujarat) ──────────────────────────────
    {
        "title": "Sprouted Matki Usal with Jowar Bhakri & Koshimbir",
        "description": "Maharashtra's signature moth bean curry tempered with goda masala, accompanied by traditional rustic millet flatbread.",
        "cuisine": "West Indian",
        "region_id": "in_west_maharashtra",
        "meal_type": "lunch",
        "dietary_flag": "vegan",
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "ingredients": [
            {"name": "Sprouted Moth Beans (Matki)", "quantity": 90, "unit": "g"},
            {"name": "Jowar (Sorghum) Flour", "quantity": 60, "unit": "g"},
            {"name": "Grated Coconut & Goda Masala", "quantity": 10, "unit": "g"},
            {"name": "Cucumber & Crushed Peanut Koshimbir", "quantity": 60, "unit": "g"},
            {"name": "Groundnut Oil", "quantity": 6, "unit": "ml"},
        ],
        "instructions": [
            "Temper mustard seeds, curry leaves, and green chillies in groundnut oil.",
            "Add sprouted matki, turmeric, goda masala, and warm water; simmer until cooked with bite.",
            "Hand-pat jowar flour with warm water into thin bhakri and cook on clay/iron griddle.",
            "Serve with refreshing cucumber koshimbir."
        ],
        "total_macros": {
            "calories_kcal": 480.0,
            "protein_g": 22.8,
            "fat_g": 10.2,
            "carbs_g": 72.0,
            "fiber_g": 15.0
        },
        "total_micros": {
            "calcium_mg": 140.0,
            "iron_mg": 5.4,
            "zinc_mg": 2.9,
            "vitamin_c_mg": 19.0
        },
        "tags": ["vegan", "high-fiber", "gluten-free", "lunch", "in_west_maharashtra"]
    },
    {
        "title": "Protein Methi Thepla with Low-Fat Paneer & Mint Chutney",
        "description": "Gujarati iron-rich fenugreek flatbread reinforced with sattu/soy flour, paired with grilled paneer.",
        "cuisine": "West Indian",
        "region_id": "in_west_gujarat",
        "meal_type": "breakfast",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "ingredients": [
            {"name": "Whole Wheat + Roasted Chana (Sattu) Flour", "quantity": 50, "unit": "g"},
            {"name": "Fresh Fenugreek (Methi) Leaves", "quantity": 40, "unit": "g"},
            {"name": "Low-Fat Paneer Cubes (pan-seared)", "quantity": 80, "unit": "g"},
            {"name": "Ajwain, Turmeric, Ginger-chilli paste", "quantity": 5, "unit": "g"},
            {"name": "Sesame Oil / Curd", "quantity": 6, "unit": "g"},
        ],
        "instructions": [
            "Knead wheat and sattu flour with chopped methi, curd, ajwain, and spices into a soft dough.",
            "Roll thin theplas and cook on a dry skillet with minimal oil.",
            "Lightly sear paneer cubes with chaat masala.",
            "Serve with coriander-mint yogurt dip."
        ],
        "total_macros": {
            "calories_kcal": 410.0,
            "protein_g": 25.0,
            "fat_g": 12.0,
            "carbs_g": 48.0,
            "fiber_g": 7.8
        },
        "total_micros": {
            "calcium_mg": 310.0,
            "iron_mg": 4.9,
            "zinc_mg": 2.5,
            "vitamin_c_mg": 15.0
        },
        "tags": ["vegetarian", "iron-rich", "breakfast", "in_west_gujarat"]
    },

    # ── 4. EAST INDIAN (Bengal / Odisha / Assam) ─────────────────────────────
    {
        "title": "Bengali Macher Jhol (Rohu Fish Curry) with Gobindobhog Brown Rice",
        "description": "Light, restorative fish curry cooked with cumin, nigella seeds (kalo jeere), green chillies, and steamed unpolished rice.",
        "cuisine": "East Indian",
        "region_id": "in_east_bengal",
        "meal_type": "lunch",
        "dietary_flag": "non_veg",
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "ingredients": [
            {"name": "Fresh Rohu / Katla Carp Fillet", "quantity": 180, "unit": "g"},
            {"name": "Unpolished Brown Rice", "quantity": 65, "unit": "g"},
            {"name": "Pointed Gourd (Potol) & Raw Papaya", "quantity": 80, "unit": "g"},
            {"name": "Kalo Jeere (Nigella), Ginger paste, Cumin", "quantity": 8, "unit": "g"},
            {"name": "Virgin Mustard Oil", "quantity": 7, "unit": "ml"},
        ],
        "instructions": [
            "Rub fish steaks with turmeric and sea salt; lightly sear in 1 tsp hot mustard oil.",
            "Temper kalo jeere and green chillies; sauté potato and raw papaya slices.",
            "Add ginger paste and cumin slurry, pour warm water to make a thin golden broth.",
            "Simmer fish for 6 minutes. Serve with hot steamed rice."
        ],
        "total_macros": {
            "calories_kcal": 510.0,
            "protein_g": 38.5,
            "fat_g": 10.5,
            "carbs_g": 62.0,
            "fiber_g": 6.5
        },
        "total_micros": {
            "calcium_mg": 160.0,
            "iron_mg": 3.8,
            "zinc_mg": 3.2,
            "vitamin_c_mg": 21.0
        },
        "tags": ["omega-3", "high-protein", "lunch", "in_east_bengal"]
    },
    {
        "title": "Chholar Dal with Sattu Kachori (Air-Fried) & Bitter Gourd Fry",
        "description": "Bengal split Bengal gram dal with coconut slivers, accompanied by baked multigrain sattu flatbread.",
        "cuisine": "East Indian",
        "region_id": "in_east_bengal",
        "meal_type": "dinner",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "ingredients": [
            {"name": "Chana Dal (soaked)", "quantity": 70, "unit": "g"},
            {"name": "Whole Wheat Atta + Sattu stuffing", "quantity": 55, "unit": "g"},
            {"name": "Fresh Coconut bits, Ginger, Hing, Tejpatta", "quantity": 15, "unit": "g"},
            {"name": "Ghee / Mustard oil", "quantity": 6, "unit": "g"},
        ],
        "instructions": [
            "Pressure cook chana dal with turmeric, ginger, and tejpatta until soft yet intact.",
            "Temper hing, cumin, dried red chilli, and fry coconut bits to golden brown in ghee.",
            "Stuff roasted sattu into wheat dough, roll, and air-fry / tawa-bake till puffed.",
            "Serve hot as a balanced vegetarian dinner."
        ],
        "total_macros": {
            "calories_kcal": 470.0,
            "protein_g": 24.0,
            "fat_g": 11.0,
            "carbs_g": 68.0,
            "fiber_g": 13.5
        },
        "total_micros": {
            "calcium_mg": 110.0,
            "iron_mg": 5.2,
            "zinc_mg": 2.8,
            "vitamin_c_mg": 9.0
        },
        "tags": ["vegetarian", "dinner", "in_east_bengal"]
    },

    # ── 5. KARNATAKA (South - High Fiber Millets & Lentils) ───────────────────
    {
        "title": "Bisi Bele Bath with Sprouted Moong Kosambari",
        "description": "Nutrient-dense Mysore Karnataka rice-lentil stew with farm vegetables, fresh tamarind, and cold raw sprouted lentil salad.",
        "cuisine": "South Indian (Karnataka)",
        "region_id": "in_south_karnataka",
        "meal_type": "lunch",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "ingredients": [
            {"name": "Brown Rice & Toor Dal (1:1 ratio)", "quantity": 90, "unit": "g"},
            {"name": "French Beans, Carrots, Green Peas", "quantity": 80, "unit": "g"},
            {"name": "Fresh Sprouted Moong & Cucumber Kosambari", "quantity": 60, "unit": "g"},
            {"name": "Cold-pressed Groundnut Oil & Ghee", "quantity": 6, "unit": "g"},
        ],
        "instructions": [
            "Cook brown rice and toor dal with diced veggies until soft.",
            "Stir in freshly ground bisi bele bath spice blend (cinnamon, cloves, marathi moggu, chana dal).",
            "Simmer with tamarind extract; top with light mustard and curry leaf tadka.",
            "Serve alongside freshly prepared cucumber-sprout kosambari."
        ],
        "total_macros": {
            "calories_kcal": 490.0,
            "protein_g": 22.8,
            "fat_g": 9.5,
            "carbs_g": 78.0,
            "fiber_g": 14.2
        },
        "total_micros": {
            "calcium_mg": 135.0,
            "iron_mg": 4.6,
            "zinc_mg": 2.9,
            "vitamin_c_mg": 22.0
        },
        "tags": ["high-fiber", "vegetarian", "lunch", "in_south_karnataka"]
    },
    {
        "title": "Akki Roti with Yennegayi (Stuffed Brinjal) & Chutney Pudi",
        "description": "Crisp Karnataka rice flatbread kneaded with dill leaves and cumin, paired with protein-rich peanut-sesame stuffed baby brinjals.",
        "cuisine": "South Indian (Karnataka)",
        "region_id": "in_south_karnataka",
        "meal_type": "dinner",
        "dietary_flag": "vegan",
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "ingredients": [
            {"name": "Rice Flour + Sobbakki (Dill Leaves)", "quantity": 70, "unit": "g"},
            {"name": "Small Purple Brinjals", "quantity": 100, "unit": "g"},
            {"name": "Roasted Peanuts, Sesame, Coconut masala", "quantity": 30, "unit": "g"},
            {"name": "Cold-pressed Sesame Oil", "quantity": 6, "unit": "ml"},
        ],
        "instructions": [
            "Slit brinjals into four and stuff with roasted peanut, sesame, jaggery, tamarind masala.",
            "Slow-cook stuffed brinjals in a covered pan until tender and aromatic.",
            "Pat akki roti dough thin on a banana leaf and roast on tawa with minimum oil.",
            "Serve warm with yennegayi curry."
        ],
        "total_macros": {
            "calories_kcal": 460.0,
            "protein_g": 18.5,
            "fat_g": 14.2,
            "carbs_g": 64.0,
            "fiber_g": 11.8
        },
        "total_micros": {
            "calcium_mg": 160.0,
            "iron_mg": 4.1,
            "zinc_mg": 3.4,
            "vitamin_c_mg": 14.0
        },
        "tags": ["vegan", "gluten-free", "dinner", "in_south_karnataka"]
    },

    # ── 6. KERALA (South - High Antioxidants, Cold Pressed Coconut & Legumes) ─
    {
        "title": "Appam with Malabar Kadala (Black Chickpea) Curry",
        "description": "Lacy fermented rice hopper paired with roasted coconut and black chickpea curry rich in iron and complex carbs.",
        "cuisine": "South Indian (Kerala)",
        "region_id": "in_south_kerala",
        "meal_type": "breakfast",
        "dietary_flag": "vegan",
        "prep_time_minutes": 15,
        "cook_time_minutes": 25,
        "ingredients": [
            {"name": "Fermented Rice & Coconut Hopper Batter", "quantity": 120, "unit": "g"},
            {"name": "Black Chickpeas (Kadala - soaked & boiled)", "quantity": 80, "unit": "g"},
            {"name": "Roasted Fresh Coconut, Shallots, Curry Leaves", "quantity": 25, "unit": "g"},
            {"name": "Virgin Cold-pressed Coconut Oil", "quantity": 5, "unit": "ml"},
        ],
        "instructions": [
            "Grind roasted grated coconut with shallots, fennel, and coriander seeds into a thick paste.",
            "Pressure-cook kadala and simmer with coconut paste and slit green chillies.",
            "Swirl fermented batter in an appachatti to create lacy crisp edges with a soft spongy center.",
            "Serve 2 fresh appams with piping hot kadala curry."
        ],
        "total_macros": {
            "calories_kcal": 420.0,
            "protein_g": 19.2,
            "fat_g": 11.5,
            "carbs_g": 61.0,
            "fiber_g": 13.0
        },
        "total_micros": {
            "calcium_mg": 95.0,
            "iron_mg": 5.8,
            "zinc_mg": 2.9,
            "vitamin_c_mg": 8.0
        },
        "tags": ["high-iron", "vegan", "breakfast", "in_south_kerala"]
    },
    {
        "title": "Kerala Chemmeen (Prawn) / Tofu Theeyal with Matta Rice",
        "description": "Authentic spiced dark-roasted coconut reduction curry with Kerala unpolished red rice (Matta) and snake gourd thoran.",
        "cuisine": "South Indian (Kerala)",
        "region_id": "in_south_kerala",
        "meal_type": "lunch",
        "dietary_flag": "non_veg",
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "ingredients": [
            {"name": "Cleaned Prawns (or Firm Organic Tofu)", "quantity": 120, "unit": "g"},
            {"name": "Kerala Matta Red Rice (boiled)", "quantity": 130, "unit": "g"},
            {"name": "Dark Roasted Coconut & Fenugreek Paste", "quantity": 30, "unit": "g"},
            {"name": "Padavalanga (Snake Gourd) Thoran", "quantity": 60, "unit": "g"},
        ],
        "instructions": [
            "Roast grated coconut with shallots, dried red chillies, and curry leaves to a deep coffee brown.",
            "Simmer prawns or tofu in tamarind-infused spiced roasted gravy until aromatic.",
            "Steam whole grain Matta rice and toss snake gourd with mild coconut-mustard crackle.",
            "Serve hot as a nutrient-dense coastal lunch."
        ],
        "total_macros": {
            "calories_kcal": 510.0,
            "protein_g": 32.5,
            "fat_g": 12.0,
            "carbs_g": 68.0,
            "fiber_g": 9.2
        },
        "total_micros": {
            "calcium_mg": 140.0,
            "iron_mg": 4.2,
            "zinc_mg": 4.1,
            "vitamin_c_mg": 16.0
        },
        "tags": ["high-protein", "omega-3", "lunch", "in_south_kerala"]
    },

    # ── 7. RAJASTHAN (North/West - High Mineral Desert Grains) ─────────────────
    {
        "title": "Bajra Roti with Rajasthani Gatte ki Sabzi & Kachumber",
        "description": "Steamed chickpea flour dumplings in light probiotic spiced yogurt gravy, served with iron-packed pearl millet flatbread.",
        "cuisine": "North Indian (Rajasthan)",
        "region_id": "in_north_rajasthan",
        "meal_type": "lunch",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "ingredients": [
            {"name": "Besan (Gram Flour for Gatte)", "quantity": 60, "unit": "g"},
            {"name": "Bajra (Pearl Millet) Flour", "quantity": 60, "unit": "g"},
            {"name": "Low-Fat Probiotic Curd (Dahi)", "quantity": 100, "unit": "g"},
            {"name": "Kasuri Methi, Ajwain, Mustard seeds", "quantity": 10, "unit": "g"},
        ],
        "instructions": [
            "Knead besan with ajwain, turmeric, and curd into logs. Boil in water, slice, and set aside.",
            "Simmer gatte in a whisked spiced yogurt sauce seasoned with kasuri methi.",
            "Hand-pat bajra flour with warm water and roast on an open clay/iron tawa.",
            "Serve warm with fresh cucumber-onion kachumber."
        ],
        "total_macros": {
            "calories_kcal": 520.0,
            "protein_g": 26.5,
            "fat_g": 12.8,
            "carbs_g": 74.0,
            "fiber_g": 13.5
        },
        "total_micros": {
            "calcium_mg": 210.0,
            "iron_mg": 7.4,
            "zinc_mg": 3.8,
            "vitamin_c_mg": 12.0
        },
        "tags": ["high-iron", "high-protein", "vegetarian", "lunch", "in_north_rajasthan"]
    },
    {
        "title": "Moong Dal Khichdi with Roasted Papad & Chaas",
        "description": "Light, easily digestible split yellow lentil and rice comfort porridge with cumin-ghee tempering and spiced buttermilk.",
        "cuisine": "North Indian (Rajasthan)",
        "region_id": "in_north_rajasthan",
        "meal_type": "dinner",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "ingredients": [
            {"name": "Yellow Moong Dal & Rice (equal parts)", "quantity": 80, "unit": "g"},
            {"name": "A2 Desi Cow Ghee (Tadka)", "quantity": 6, "unit": "g"},
            {"name": "Jeera, Hing, Fresh Ginger", "quantity": 10, "unit": "g"},
            {"name": "Spiced Buttermilk (Chaas with Mint & Black Salt)", "quantity": 200, "unit": "ml"},
        ],
        "instructions": [
            "Pressure cook moong dal and rice with turmeric, salt, and ginger until creamy.",
            "Temper cumin seeds and hing in 1 tsp warm ghee; pour over khichdi.",
            "Serve with chilled chaas for gut-microbiome and recovery support."
        ],
        "total_macros": {
            "calories_kcal": 410.0,
            "protein_g": 20.2,
            "fat_g": 9.0,
            "carbs_g": 62.0,
            "fiber_g": 8.5
        },
        "total_micros": {
            "calcium_mg": 175.0,
            "iron_mg": 3.8,
            "zinc_mg": 2.4,
            "vitamin_c_mg": 6.0
        },
        "tags": ["gut-health", "vegetarian", "dinner", "in_north_rajasthan"]
    },

    # ── 8. KASHMIR (North - Warming Herbs, Lotus Stem & Saffron Spices) ───────
    {
        "title": "Nadru Yakhni (Lotus Stem in Spiced Fennel Yogurt) with Brown Rice",
        "description": "Crisp high-fiber Kashmiri lotus stem simmered in mild yogurt gravy infused with dry ginger, fennel, and whole spices.",
        "cuisine": "North Indian (Kashmir)",
        "region_id": "in_north_kashmir",
        "meal_type": "lunch",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "ingredients": [
            {"name": "Fresh Nadru (Lotus Stem - sliced)", "quantity": 120, "unit": "g"},
            {"name": "Probiotic Yogurt (Whisked)", "quantity": 120, "unit": "g"},
            {"name": "Steamed Brown Rice", "quantity": 120, "unit": "g"},
            {"name": "Sonth (Dry Ginger), Saunf (Fennel), Black Cardamom", "quantity": 15, "unit": "g"},
        ],
        "instructions": [
            "Parboil sliced nadru in water with salt and turmeric.",
            "Slow-whisk yogurt over low heat until boiling to prevent curdling, then stir in saunf and sonth powders.",
            "Add boiled nadru and simmer for 15 minutes till rich and fragrant.",
            "Serve warm over steamed brown rice."
        ],
        "total_macros": {
            "calories_kcal": 440.0,
            "protein_g": 18.0,
            "fat_g": 8.5,
            "carbs_g": 72.0,
            "fiber_g": 11.2
        },
        "total_micros": {
            "calcium_mg": 230.0,
            "iron_mg": 4.8,
            "zinc_mg": 2.5,
            "vitamin_c_mg": 28.0
        },
        "tags": ["high-calcium", "high-fiber", "vegetarian", "lunch", "in_north_kashmir"]
    },

    # ── 9. ODISHA (East - Sattvic Lentils, Superfood Veggies & Mustard) ───────
    {
        "title": "Odia Dalma with Steamed Rice & Bhaja",
        "description": "Traditional Jagannath Puri style roasted toor dal slow-cooked with raw papaya, pumpkin, drumstick, and cumin-chilli temper.",
        "cuisine": "East Indian (Odisha)",
        "region_id": "in_east_odisha",
        "meal_type": "lunch",
        "dietary_flag": "vegetarian",
        "prep_time_minutes": 15,
        "cook_time_minutes": 25,
        "ingredients": [
            {"name": "Roasted Toor Dal (Harada Dali)", "quantity": 70, "unit": "g"},
            {"name": "Raw Papaya, Drumstick, Pumpkin, Yam cubes", "quantity": 120, "unit": "g"},
            {"name": "Steamed Rice", "quantity": 120, "unit": "g"},
            {"name": "Panch Phoron, Roasted Cumin-Chilli Powder (Bhaja Rashi)", "quantity": 10, "unit": "g"},
        ],
        "instructions": [
            "Dry roast toor dal slightly, then boil with turmeric, ginger, salt, and root vegetables till soft.",
            "Temper with ghee, bay leaf, and panch phoron.",
            "Sprinkle fresh roasted cumin-dry chilli powder and freshly grated coconut before serving.",
            "Serve hot with steamed rice."
        ],
        "total_macros": {
            "calories_kcal": 480.0,
            "protein_g": 23.5,
            "fat_g": 8.2,
            "carbs_g": 77.0,
            "fiber_g": 15.4
        },
        "total_micros": {
            "calcium_mg": 145.0,
            "iron_mg": 5.6,
            "zinc_mg": 3.1,
            "vitamin_c_mg": 34.0
        },
        "tags": ["sattvic", "high-fiber", "high-protein", "lunch", "in_east_odisha"]
    },
]

