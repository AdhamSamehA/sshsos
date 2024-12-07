from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from server.dependencies import get_db
from server.schemas import SupermarketFeedResponse

router = APIRouter()

@router.get("/supermarket/feed", response_model=SupermarketFeedResponse)
async def get_supermarket_feed(db: AsyncSession = Depends(get_db)) -> SupermarketFeedResponse:
    """
    Overview:
    Fetch a list of supermarkets with their basic details.

    Function Logic:
    1. Query the database to retrieve supermarket details.
    2. Filter active supermarkets if needed.
    3. Return the supermarket data for the frontend.

    Parameters:
    - db (AsyncSession): Database session for querying data.

    Returns:
    - SupermarketFeedResponse: Encapsulated list of supermarkets.
    """
    # Mock response for frontend testing
    return SupermarketFeedResponse(
        success=True,
        supermarkets=[
            {
                "id": 1,
                "name": "Supermarket A",
                "address": "123 Main St, City",
                "phone_number": "123-456-7890",
                "photo_url": "https://www.dealzbook.ae/filemanager/uploads/myviva-logo.webp"
            },
            {
                "id": 2,
                "name": "Supermarket B",
                "address": "456 Elm St, Town",
                "phone_number": "987-654-3210",
                "photo_url": "https://t4.ftcdn.net/jpg/02/98/00/31/360_F_298003130_m46tOGOvzZjxXjP61HjVxY5awE9qU406.jpg"
            }
        ]
    )
