from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId
from ..models.recipe import Recipe, RecipeIngredient
from ..models.food_item import Macronutrients, Micronutrients
from ..schemas.recipe_schemas import RecipeSearchRequest, RecipeSummary, CreateRecipeRequest, UpdateRecipeRequest
from ..data.regional_seeds import REGIONAL_RECIPES_SEED

# Fallback memory registry for sub-50ms query latency when MongoDB is offline
_memory_recipes: List[Dict[str, Any]] = list(REGIONAL_RECIPES_SEED)


async def seed_regional_recipes_if_empty() -> int:
    """Auto-seeds authentic IFCT-grounded regional recipes into database on startup."""
    try:
        count = await Recipe.count()
        if count == 0:
            for item in REGIONAL_RECIPES_SEED:
                macros = Macronutrients(**item["total_macros"])
                micros = Micronutrients(**item["total_micros"])
                ingredients = [
                    RecipeIngredient(name=ing["name"], quantity=float(ing["quantity"]), unit=ing["unit"])
                    for ing in item.get("ingredients", [])
                ]
                recipe = Recipe(
                    title=item["title"],
                    description=item["description"],
                    cuisine=item["cuisine"],
                    region_id=item.get("region_id", "in_general"),
                    meal_type=item.get("meal_type", "lunch"),
                    dietary_flag=item.get("dietary_flag", "vegetarian"),
                    prep_time_minutes=item["prep_time_minutes"],
                    cook_time_minutes=item["cook_time_minutes"],
                    ingredients=ingredients,
                    instructions=item["instructions"],
                    total_macros=macros,
                    total_micros=micros,
                    tags=item.get("tags", []),
                )
                await recipe.insert()
            print(f"✅ Seeded {len(REGIONAL_RECIPES_SEED)} authentic regional recipes into MongoDB.")
            return len(REGIONAL_RECIPES_SEED)
        return count
    except Exception as e:
        print(f"[Recipe] Note: DB seeding skipped (MongoDB offline / in-memory mode active): {e}")
        return len(_memory_recipes)


async def search_recipes(req: RecipeSearchRequest) -> List[RecipeSummary]:
    try:
        query: dict = {}
        if req.cuisine:
            query["cuisine"] = req.cuisine
        if req.max_prep_time:
            query["prep_time_minutes"] = {"$lte": req.max_prep_time}
        if req.tags:
            query["tags"] = {"$all": req.tags}

        recipes = await Recipe.find(query).to_list()
        if recipes:
            return [
                RecipeSummary(
                    id=str(r.id),
                    title=r.title,
                    cuisine=r.cuisine,
                    prep_time_minutes=r.prep_time_minutes,
                    cook_time_minutes=r.cook_time_minutes,
                    total_macros=r.total_macros,
                    tags=r.tags
                )
                for r in recipes
            ]
    except Exception:
        pass

    # High-speed in-memory filtered return
    results = []
    for r in _memory_recipes:
        if req.cuisine and req.cuisine.lower() not in r["cuisine"].lower():
            continue
        if req.max_prep_time and r["prep_time_minutes"] > req.max_prep_time:
            continue
        if req.tags and not all(t in r.get("tags", []) for t in req.tags):
            continue
        results.append(
            RecipeSummary(
                id=r["title"],
                title=r["title"],
                cuisine=r["cuisine"],
                prep_time_minutes=r["prep_time_minutes"],
                cook_time_minutes=r["cook_time_minutes"],
                total_macros=Macronutrients(**r["total_macros"]),
                tags=r.get("tags", [])
            )
        )
    return results


async def get_recipe_by_id(recipe_id: str) -> Optional[Recipe]:
    try:
        return await Recipe.get(PydanticObjectId(recipe_id))
    except Exception:
        pass
    for r in _memory_recipes:
        if r["title"] == recipe_id or r.get("id") == recipe_id:
            return Recipe(
                title=r["title"],
                description=r["description"],
                cuisine=r["cuisine"],
                region_id=r.get("region_id", "in_general"),
                meal_type=r.get("meal_type", "lunch"),
                dietary_flag=r.get("dietary_flag", "vegetarian"),
                prep_time_minutes=r["prep_time_minutes"],
                cook_time_minutes=r["cook_time_minutes"],
                ingredients=[RecipeIngredient(name=i["name"], quantity=i["quantity"], unit=i["unit"]) for i in r.get("ingredients", [])],
                instructions=r["instructions"],
                total_macros=Macronutrients(**r["total_macros"]),
                total_micros=Micronutrients(**r["total_micros"]),
                tags=r.get("tags", [])
            )
    return None


async def list_all_recipes() -> List[RecipeSummary]:
    try:
        recipes = await Recipe.find_all().to_list()
        if recipes:
            return [
                RecipeSummary(
                    id=str(r.id),
                    title=r.title,
                    cuisine=r.cuisine,
                    prep_time_minutes=r.prep_time_minutes,
                    cook_time_minutes=r.cook_time_minutes,
                    total_macros=r.total_macros,
                    tags=r.tags
                )
                for r in recipes
            ]
    except Exception:
        pass
    return [
        RecipeSummary(
            id=r["title"],
            title=r["title"],
            cuisine=r["cuisine"],
            prep_time_minutes=r["prep_time_minutes"],
            cook_time_minutes=r["cook_time_minutes"],
            total_macros=Macronutrients(**r["total_macros"]),
            tags=r.get("tags", [])
        )
        for r in _memory_recipes
    ]


async def create_recipe(req: CreateRecipeRequest) -> Recipe:
    macros = Macronutrients(
        calories_kcal=req.total_macros.calories_kcal,
        protein_g=req.total_macros.protein_g,
        fat_g=req.total_macros.fat_g,
        carbs_g=req.total_macros.carbs_g,
        fiber_g=req.total_macros.fiber_g,
    )
    micros = Micronutrients()

    recipe = Recipe(
        title=req.title,
        description=req.description,
        cuisine=req.cuisine,
        prep_time_minutes=req.prep_time_minutes,
        cook_time_minutes=req.cook_time_minutes,
        ingredients=[],
        instructions=req.instructions,
        total_macros=macros,
        total_micros=micros,
        tags=req.tags,
        image_url=req.image_url,
    )
    try:
        await recipe.insert()
    except Exception:
        pass
    return recipe


async def update_recipe(recipe_id: str, req: UpdateRecipeRequest) -> Optional[Recipe]:
    try:
        recipe = await Recipe.get(PydanticObjectId(recipe_id))
        if not recipe:
            return None
        update_data = req.model_dump(exclude_unset=True)
        if "total_macros" in update_data and update_data["total_macros"] is not None:
            macros_data = update_data.pop("total_macros")
            recipe.total_macros = Macronutrients(**macros_data)
        for field, value in update_data.items():
            setattr(recipe, field, value)
        await recipe.save()
        return recipe
    except Exception:
        return None


async def delete_recipe(recipe_id: str) -> bool:
    try:
        recipe = await Recipe.get(PydanticObjectId(recipe_id))
        if not recipe:
            return False
        await recipe.delete()
        return True
    except Exception:
        return False
