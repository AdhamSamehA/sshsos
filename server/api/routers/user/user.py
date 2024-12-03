from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from server.schemas import AccountDetailsResponse, OrderHistoryResponse, OrderSummary
from server.dependencies import get_db

router = APIRouter()

@router.get("/user/account", response_model=AccountDetailsResponse)
async def get_account_details(user_id: int, db: AsyncSession = Depends(get_db)) -> AccountDetailsResponse:
    """
    Overview:
    Fetch account details for a user.

    Function Logic:
    1. Fetch wallet balance for the user.
    2. Retrieve the default address (building name).
    3. Count the number of past orders.

    Parameters:
    - user_id (int): The ID of the user.
    - db (AsyncSession): Database session for querying data.

    Returns:
    - AccountDetailsResponse: Wallet balance, default address, total orders.
    """
    # Mock response for frontend testing
    return AccountDetailsResponse(
        wallet_balance=250.0,
        default_address="Building A, Apartment 101",
        total_orders=15
    )

@router.get("/user/orders", response_model=OrderHistoryResponse)
async def get_user_order_history(user_id: int, db: AsyncSession = Depends(get_db)) -> OrderHistoryResponse:
    """
    Overview:
    Fetch the order history for a user.

    Function Logic:
    1. Query the database for all orders placed by the user.
    2. Return a list of orders with details.

    Parameters:
    - user_id (int): The ID of the user.
    - db (AsyncSession): Database session for querying data.

    Returns:
    - OrderHistoryResponse: A list of past orders.
    """
    # Mock response for frontend testing
    return OrderHistoryResponse(
        user_id=user_id,
        orders=[
            OrderSummary(order_id=101, date="2024-12-01T10:00:00", total_amount=50.0, status="completed"),
            OrderSummary(order_id=102, date="2024-12-02T14:00:00", total_amount=75.0, status="pending"),
            OrderSummary(order_id=103, date="2024-12-03T08:00:00", total_amount=30.0, status="cancelled")
        ]
    )

