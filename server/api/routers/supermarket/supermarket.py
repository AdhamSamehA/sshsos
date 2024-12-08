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
        SupermarketResponse(
            id=supermarket.id,
            name=supermarket.name,
            address=supermarket.address,
            phone_number=supermarket.phone_number,
            photo_url=supermarket.photo_url
        ).dict()
        for supermarket in supermarkets
    ]
)
