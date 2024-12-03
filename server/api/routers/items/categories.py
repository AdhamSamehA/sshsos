from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from server.schemas import CategoryResponse
from server.dependencies import get_db
from typing import List

router = APIRouter()

@router.get("/items/categories", response_model=List[CategoryResponse])
async def get_categories_by_supermarket(
    supermarket_id: int = Query(..., description="ID of the supermarket to filter categories")
) -> List[CategoryResponse]:
    """
    Fetch categories available in a specific supermarket (mock response).
    """
    # Mock response for frontend testing
    return [
        CategoryResponse(id=1, name="Dairy & Eggs"),
        CategoryResponse(id=2, name="Fruits & Vegetables"),
        CategoryResponse(id=3, name="Bakery")
    ]

