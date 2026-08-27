from fastapi import APIRouter, Depends
from typing import Dict, Any, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.grocery_schemas import AddItemRequest, GroceryListResponse, GroceryItemResponse, ToggleItemRequest
from ..services.grocery_service import get_list, add_item, toggle_item, delete_item, clear_checked, get_db

from nutriplan_shared.auth import get_current_user, user_uuid

router = APIRouter(prefix="/api/v1/grocery", tags=["Grocery"])


@router.get("/list", response_model=GroceryListResponse, summary="Get grocery list")
async def get_grocery_list(user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_list(user_uuid(user), db)


@router.post("/items", response_model=GroceryItemResponse, status_code=201, summary="Add item")
async def add_grocery_item(req: AddItemRequest, user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await add_item(user_uuid(user), req, db)


@router.patch("/items/{item_id}/toggle", response_model=GroceryItemResponse, summary="Check/uncheck item")
async def toggle_grocery_item(item_id: uuid.UUID, req: ToggleItemRequest, user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await toggle_item(item_id, req.is_checked, user_uuid(user), db)


@router.delete("/items/{item_id}", status_code=204, summary="Delete item")
async def delete_grocery_item(item_id: uuid.UUID, user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await delete_item(item_id, user_uuid(user), db)


@router.delete("/clear-checked", status_code=204, summary="Clear all checked items")
async def clear_checked_items(user: Dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await clear_checked(user_uuid(user), db)


@router.post("/generate-from-plan", summary="Auto-generate grocery list from regional meal plan")
async def generate_grocery_from_plan(
    req: "GenerateFromPlanRequest",
    user: Dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Calls the Regional Meal Plan Engine, extracts all ingredients,
    deduplicates and categorizes them, then persists to the user's grocery list.
    """
    import httpx
    from ..schemas.grocery_schemas import GenerateFromPlanRequest, RegionalGroceryGroupedResponse
    from ..services.regional_grocery_aggregator import aggregate_ingredients_from_plan, group_by_category
    from ..services.grocery_service import get_or_create_list, AsyncSessionLocal
    import uuid as uuid_lib

    # 1. Request a regional meal plan from the Meal Plan Service
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "http://localhost:8009/api/v1/plan/generate/regional",
                json={
                    "user_id": str(user_uuid(user)),
                    "caloric_target": req.caloric_target,
                    "regional_preference": req.regional_preference,
                    "dietary_flag": req.dietary_flag,
                }
            )
            plan_data = resp.json()
            plan = plan_data.get("plan", {})
    except Exception as e:
        return {"error": f"Could not fetch meal plan: {str(e)}"}

    # 2. Extract & aggregate ingredients
    flat_ingredients = aggregate_ingredients_from_plan(plan)
    grouped = group_by_category(flat_ingredients)

    # 3. Persist to DB (clear existing if replace_existing)
    uid = user_uuid(user)
    grocery_list = await get_or_create_list(uid, db)
    if req.replace_existing:
        from sqlalchemy import delete as sql_delete
        from ..models.grocery import GroceryItem
        await db.execute(sql_delete(GroceryItem).where(GroceryItem.list_id == grocery_list.id))
        await db.commit()

    # Bulk-insert new items
    from ..models.grocery import GroceryItem
    for ing in flat_ingredients:
        item = GroceryItem(
            id=uuid_lib.uuid4(),
            list_id=grocery_list.id,
            name=ing["name"],
            quantity=str(round(ing["quantity"], 1)),
            unit=ing["unit"],
            category=ing["category"],
        )
        db.add(item)
    await db.commit()

    return RegionalGroceryGroupedResponse(
        total_items=len(flat_ingredients),
        categories=grouped,
        plan_summary={
            "meals": [m.get("name") for m in plan.get("meals", [])],
            "total_calories": plan.get("total_calories"),
            "regional_preference": req.regional_preference,
        },
    )
