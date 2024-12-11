from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.models import Supermarket
from typing import List
from server.dependencies import get_db
from server.schemas import SupermarketFeedResponse, SupermarketResponse
from loguru import logger  # Added loguru for logging

router = APIRouter()

@router.get("/supermarket/feed", response_model=SupermarketFeedResponse)
async def get_supermarket_feed(
    db: AsyncSession = Depends(get_db)
) -> SupermarketFeedResponse:
    """
    Fetch a list of supermarkets with their basic details.
    """
    logger.info("Fetching supermarket feed")
    try:
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
            logger.warning("No supermarkets found")
            return SupermarketFeedResponse(success=True, supermarkets=[])

        formatted_supermarkets = [
            {
                "id": supermarket.id,
                "name": supermarket.name,
                "address": supermarket.address,
                "phone_number": supermarket.phone_number,
                "photo_url": supermarket.photo_url,
            }
            for supermarket in supermarkets
        ]

        logger.info(f"Fetched {len(supermarkets)} supermarkets successfully")
        # Return the formatted response
        return SupermarketFeedResponse(
            success=True,
            supermarkets=formatted_supermarkets
        )
    except Exception as e:
        logger.error(f"Failed to fetch supermarket feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch supermarket feed")
