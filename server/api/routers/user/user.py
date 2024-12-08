from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from server.schemas import AccountDetailsResponse, OrderHistoryResponse, OrderSummary
from server.models import User, WalletTransaction, Order, Address
from server.dependencies import get_db

router = APIRouter()

@router.get("/user/account", response_model=AccountDetailsResponse)
async def get_account_details(user_id: int, db: AsyncSession = Depends(get_db)) -> AccountDetailsResponse:
    """
    Overview:
    Fetch account details for a user.

    Function Logic:
    1. Fetch wallet balance for the user.
    2. Retrieve the default address (building name) based on default_address_id.
    3. Count the number of past orders.

    Parameters:
    - user_id (int): The ID of the user.
    - db (AsyncSession): Database session for querying data.

    Returns:
    - AccountDetailsResponse: Wallet balance, default address, total orders.
    """
    try:
        # Fetch user details including default_address_id
        stmt_user = select(User).options(selectinload(User.wallet)).where(User.id == user_id)
        user_result = await db.execute(stmt_user)
        user = user_result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Fetch wallet balance
        if not user.wallet:
            wallet_balance = 0.0
        else:
            stmt_wallet = select(func.sum(WalletTransaction.amount)).where(WalletTransaction.wallet_id == user.wallet.id)
            wallet_result = await db.execute(stmt_wallet)
            wallet_balance = wallet_result.scalar() or 0.0

        # Retrieve default address building name
        default_address = "No default address set"
        if user.default_address_id:
            stmt_address = select(Address.building_name).where(Address.id == user.default_address_id)
            address_result = await db.execute(stmt_address)
            address = address_result.scalar()
            if address:
                default_address = address

        # Count the number of past orders
        stmt_orders = select(func.count(Order.id)).where(Order.user_id == user_id)
        orders_result = await db.execute(stmt_orders)
        total_orders = orders_result.scalar() or 0

        # Return response
        return AccountDetailsResponse(
            wallet_balance=wallet_balance,
            default_address=default_address,
            total_orders=total_orders
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch account details: {str(e)}")