from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from server.schemas import CategoryResponse
from server.models import Category, SupermarketCategory
from server.dependencies import get_db
from typing import List
from loguru import logger

router = APIRouter()

@router.get("/items/categories", response_model=List[CategoryResponse])
async def get_categories_by_supermarket(
    supermarket_id: int = Query(..., description="ID of the supermarket to filter categories"),
    db: AsyncSession = Depends(get_db),
) -> List[CategoryResponse]:
    """
    Fetch categories available in a specific supermarket (mock response).
    """
    logger.info(f"Fetching categories for supermarket_id={supermarket_id}")
    try:
        # Query to join categories and supermarket_categories
        query = (
            select(Category.id, Category.name)
            .join(SupermarketCategory, SupermarketCategory.category_id == Category.id)
            .where(SupermarketCategory.supermarket_id == supermarket_id)
        )

        # Execute query
        result = await db.execute(query)
        categories = result.fetchall()

        # Check if any categories are returned
        if not categories:
            logger.warning(f"No categories found for supermarket_id={supermarket_id}")
            raise HTTPException(status_code=404, detail="No categories found for this supermarket.")

        logger.info(f"Categories fetched successfully for supermarket_id={supermarket_id}, count={len(categories)}")
        # Return categories as a list of CategoryResponse
        return [CategoryResponse(id=cat.id, name=cat.name) for cat in categories]
    except Exception as e:
        logger.error(f"Error fetching categories for supermarket_id={supermarket_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")