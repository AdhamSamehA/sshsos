from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from server.models import Supermarket
from typing import List
from server.dependencies import get_db
from server.schemas import SupermarketFeedResponse, SupermarketResponse, AddSupermarketRequest

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
                "photo_url": "https://example.com/supermarket_a.jpg"
            },
            {
                "id": 2,
                "name": "Supermarket B",
                "address": "456 Elm St, Town",
                "phone_number": "987-654-3210",
                "photo_url": "https://example.com/supermarket_b.jpg"
            }
        ]
    )

@router.post("/admin/supermarkets", response_model=SupermarketResponse)
async def add_supermarket(
    request: AddSupermarketRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Admin-only endpoint to add a supermarket.

    Parameters:
    - request (AddSupermarketRequest): Supermarket details to add.
    - db (AsyncSession): Database session.
    - admin_user (dict): User information, validated as admin.

    Returns:
    - SupermarketResponse: Details of the newly added supermarket.
    """
    # Create a new supermarket instance
    new_supermarket = Supermarket(
        name=request.name,
        photo_url=request.photo_url,
        address=request.address,
        phone_number=request.phone_number
    )

    # Add to the database
    db.add(new_supermarket)
    await db.commit()
    await db.refresh(new_supermarket)

    return SupermarketResponse(
        id=new_supermarket.id,
        name=new_supermarket.name,
        photo_url=new_supermarket.photo_url,
        address=new_supermarket.address,
        phone_number=new_supermarket.phone_number
    )