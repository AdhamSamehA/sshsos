from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from server.models import Item, Category
from server.schemas import ItemListResponse, ItemResponse
from server.dependencies import get_db

router = APIRouter()

@router.get("/items", response_model=ItemListResponse)
async def get_items_by_category_and_supermarket(
    category_id: int = Query(..., description="ID of the category to filter items"),
    supermarket_id: int = Query(..., description="ID of the supermarket to filter items"),
    db: AsyncSession = Depends(get_db),
) -> ItemListResponse:
    """
    Fetch items for a given category and supermarket.
    """
    # Query to fetch items based on category and supermarket
    query = (
        select(Item.id, Item.name, Item.photo_url, Item.price, Item.description, Item.supermarket_id)
        .where(Item.category_id == category_id, Item.supermarket_id == supermarket_id)
    )

    # Execute the query
    result = await db.execute(query)
    items = result.fetchall()

    # Raise error if no items are found
    if not items:
        raise HTTPException(status_code=404, detail="No items found for the given category and supermarket.")

    # Fetch category name
    category_query = select(Category.name).where(Category.id == category_id)
    category_result = await db.execute(category_query)
    category_name = category_result.scalar()

    if not category_name:
        raise HTTPException(status_code=404, detail="Category not found.")

    # Build the response
    return ItemListResponse(
        category_id=category_id,
        category_name=category_name,
        items=[
            ItemResponse(
                id=item.id,
                name=item.name,
                photo_url=item.photo_url,
                price=item.price,
                description=item.description,
                supermarket_id=item.supermarket_id
            )
            for item in items
        ]
    )
