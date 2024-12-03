from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from server.schemas import WalletTopUpRequest, WalletPaymentRequest, WalletResponse
from server.dependencies import get_db
from server.models.wallet import Wallet

router = APIRouter()

@router.post("/wallet/top-up", response_model=WalletResponse)
async def top_up_wallet(request: WalletTopUpRequest, db: AsyncSession = Depends(get_db)) -> WalletResponse:
    """
    Overview:
    Top up the user's wallet with the specified amount.

    Function Logic:
    1. Accepts the amount to be added as input.
    2. Fetches the wallet from the database.
    3. Updates the wallet balance with the new amount.
    4. Returns the updated wallet balance and a success message.

    Parameters:
    - request (WalletTopUpRequest): Contains the amount to add to the wallet.
    - db (AsyncSession): The database session dependency for querying and updating data.

    Returns:
    - A JSON response conforming to the WalletResponse model.
    """
    # Mock response for frontend testing
    return WalletResponse(
        wallet_id=1,
        balance=150.0,
        message="Wallet topped up successfully."
    )


@router.post("/wallet/pay", response_model=WalletResponse)
async def pay_from_wallet(request: WalletPaymentRequest, db: AsyncSession = Depends(get_db)) -> WalletResponse:
    """
    Overview:
    Deduct a specified amount from the user's wallet balance.

    Function Logic:
    1. Accepts the amount to deduct as input.
    2. Fetches the wallet from the database.
    3. Checks if the wallet has sufficient balance.
    4. Deducts the amount from the wallet.
    5. Returns the updated wallet balance and a success message.

    Parameters:
    - request (WalletPaymentRequest): Contains the amount to deduct from the wallet.
    - db (AsyncSession): The database session dependency for querying and updating data.

    Returns:
    - A JSON response conforming to the WalletResponse model.
    """
    # Mock response for frontend testing
    return WalletResponse(
        wallet_id=1,
        balance=120.0,
        message="Payment successful."
    )


@router.get("/wallet/balance", response_model=WalletResponse)
async def check_wallet_balance(wallet_id: int, db: AsyncSession = Depends(get_db)) -> WalletResponse:
    """
    Overview:
    Retrieve the current balance of the user's wallet.

    Function Logic:
    1. Accepts wallet ID as input.
    2. Fetches the wallet balance from the database.
    3. Returns the wallet balance and a success message.

    Parameters:
    - wallet_id (int): The ID of the wallet to retrieve.
    - db (AsyncSession): The database session dependency for querying data.

    Returns:
    - A JSON response conforming to the WalletResponse model.
    """
    # Mock response for frontend testing
    return WalletResponse(
        wallet_id=wallet_id,
        balance=100.0,
        message="Wallet balance retrieved successfully."
    )

