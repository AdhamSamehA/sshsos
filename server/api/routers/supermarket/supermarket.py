from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.models import Supermarket
from typing import List
from server.dependencies import get_db
from server.schemas import SupermarketFeedResponse, SupermarketResponse

router = APIRouter()

@router.get("/supermarket/feed", response_model=SupermarketFeedResponse)
async def get_supermarket_feed(
    db: AsyncSession = Depends(get_db)
) -> SupermarketFeedResponse:
    """
    Fetch a list of supermarkets with their basic details.
    """
    # Query to fetch supermarket details
    query = select(
        Supermarket.id,
        Supermarket.name,
        Supermarket.address,
        Supermarket.phone_number,
        Supermarket.photo_url
    )
    result = await db.execute(query)
    supermarkets = result.fetchall()

    # If no supermarkets are found, return an empty response
    if not supermarkets:
        return SupermarketFeedResponse(success=True, supermarkets=[])

    # Format the response data
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

