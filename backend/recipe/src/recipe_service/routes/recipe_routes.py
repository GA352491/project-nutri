from fastapi import APIRouter, HTTPException, status
from typing import List
from ..schemas.recipe_schemas import (
    RecipeSearchRequest, RecipeSummary,
    CreateRecipeRequest, UpdateRecipeRequest
)
from ..models.recipe import Recipe
from ..services.recipe_service import (
    search_recipes, get_recipe_by_id, list_all_recipes,
    create_recipe, update_recipe, delete_recipe
)

router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])

@router.get(
    "/",
    response_model=List[RecipeSummary],
    summary="List all recipes (Admin)"
)
async def list_recipes():
    return await list_all_recipes()

@router.post(
    "/search",
    response_model=List[RecipeSummary],
    summary="Search recipes"
)
async def search(req: RecipeSearchRequest):
    return await search_recipes(req)

@router.get(
    "/{recipe_id}",
    response_model=Recipe,
    summary="Get full recipe details"
)
async def get_recipe(recipe_id: str):
    recipe = await get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe

@router.post(
    "/",
    response_model=Recipe,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recipe (Admin)"
)
async def create(req: CreateRecipeRequest):
    return await create_recipe(req)

@router.put(
    "/{recipe_id}",
    response_model=Recipe,
    summary="Update a recipe (Admin)"
)
async def update(recipe_id: str, req: UpdateRecipeRequest):
    recipe = await update_recipe(recipe_id, req)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe

@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a recipe (Admin)"
)
async def delete(recipe_id: str):
    success = await delete_recipe(recipe_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
