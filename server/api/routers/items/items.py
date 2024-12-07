from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from server.schemas import ItemListResponse, ItemResponse
from server.dependencies import get_db

router = APIRouter()

@router.get("/items", response_model=ItemListResponse)
async def get_items_by_category_and_supermarket(
    category_id: int = Query(..., description="ID of the category to filter items"),
    supermarket_id: int = Query(..., description="ID of the supermarket to filter items")
) -> ItemListResponse:
    """
    Fetch items for a given category and supermarket (mock response).
    """
    # Mock response for frontend testing
    return ItemListResponse(
        category_id=category_id,
        category_name="Dairy & Eggs",  # Mock category name
        items=[
            ItemResponse(
                id=1,
                name="Milk",
                photo_url="https://cdn.theatlantic.com/thumbor/MAp_MfXXLZpH6CyMHf9LfaJjdnM=/458x43:1523x1108/540x540/media/img/mt/2024/10/Atlantic_Milk_2000x1125/original.jpg",
                price=5.0,
                description="Fresh milk from local farms.",
                supermarket_id=supermarket_id
            ),
            ItemResponse(
                id=2,
                name="Cheese",
                photo_url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTXhle2NDAmRQVL_u0WqGO7A6kxdisfpCxj-Q&s",
                price=7.0,
                description="Delicious cheddar cheese.",
                supermarket_id=supermarket_id
            )
        ]
    )
