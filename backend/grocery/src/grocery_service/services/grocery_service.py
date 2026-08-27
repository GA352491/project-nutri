import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from fastapi import HTTPException

from ..models.grocery import Base, GroceryList, GroceryItem
from ..schemas.grocery_schemas import AddItemRequest, GroceryListResponse, GroceryItemResponse
from ..config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_or_create_list(user_id: uuid.UUID, db: AsyncSession) -> GroceryList:
    result = await db.execute(select(GroceryList).where(GroceryList.user_id == user_id))
    grocery_list = result.scalars().first()
    if not grocery_list:
        grocery_list = GroceryList(user_id=user_id, name="My Grocery List")
        db.add(grocery_list)
        await db.commit()
        await db.refresh(grocery_list)
    return grocery_list


async def get_list(user_id: uuid.UUID, db: AsyncSession) -> GroceryListResponse:
    if not db:
        async with AsyncSessionLocal() as session:
            return await get_list(user_id, session)

    grocery_list = await get_or_create_list(user_id, db)
    result = await db.execute(select(GroceryItem).where(GroceryItem.list_id == grocery_list.id))
    items = result.scalars().all()
    return GroceryListResponse(
        id=grocery_list.id,
        user_id=grocery_list.user_id,
        name=grocery_list.name,
        items=[GroceryItemResponse.model_validate(i) for i in items]
    )


async def add_item(user_id: uuid.UUID, req: AddItemRequest, db: AsyncSession) -> GroceryItemResponse:
    if not db:
        async with AsyncSessionLocal() as session:
            return await add_item(user_id, req, session)

    new_id = uuid.uuid4()
    grocery_list = await get_or_create_list(user_id, db)
    item = GroceryItem(
        id=new_id,
        list_id=grocery_list.id,
        name=req.name,
        quantity=req.quantity,
        unit=req.unit,
        category=req.category,
        source_recipe_id=req.source_recipe_id,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return GroceryItemResponse.model_validate(item)


async def toggle_item(item_id: uuid.UUID, is_checked: bool, user_id: uuid.UUID, db: AsyncSession) -> GroceryItemResponse:
    if not db:
        async with AsyncSessionLocal() as session:
            return await toggle_item(item_id, is_checked, user_id, session)

    result = await db.execute(
        select(GroceryItem)
        .join(GroceryList)
        .where(GroceryItem.id == item_id, GroceryList.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Grocery item not found")

    item.is_checked = is_checked
    await db.commit()
    await db.refresh(item)
    return GroceryItemResponse.model_validate(item)


async def delete_item(item_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> None:
    if not db:
        async with AsyncSessionLocal() as session:
            return await delete_item(item_id, user_id, session)

    result = await db.execute(
        select(GroceryItem)
        .join(GroceryList)
        .where(GroceryItem.id == item_id, GroceryList.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if item:
        await db.delete(item)
        await db.commit()


async def clear_checked(user_id: uuid.UUID, db: AsyncSession) -> None:
    if not db:
        async with AsyncSessionLocal() as session:
            return await clear_checked(user_id, session)

    grocery_list = await get_or_create_list(user_id, db)
    result = await db.execute(
        select(GroceryItem).where(
            GroceryItem.list_id == grocery_list.id,
            GroceryItem.is_checked == True
        )
    )
    for item in result.scalars().all():
        await db.delete(item)
    await db.commit()
