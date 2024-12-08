from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime

from server.schemas import WalletTopUpRequest, WalletPaymentRequest, WalletResponse
from server.dependencies import get_db
from server.models import Wallet, WalletTransaction, User
from server.models.wallet_transaction import TransactionType


router = APIRouter()

@router.post("/wallet/top-up", response_model=WalletResponse)
async def top_up_wallet(request: WalletTopUpRequest, db: AsyncSession = Depends(get_db)) -> WalletResponse:
    """
    Top up the user's wallet with the specified amount.
    """
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Top-up amount must be greater than zero.")

    # Fetch the user with the wallet eagerly loaded
    stmt = select(User).options(selectinload(User.wallet)).where(User.id == request.user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not user.wallet:
        raise HTTPException(status_code=404, detail="User or wallet not found.")

    wallet = user.wallet

    # Add a credit transaction
    transaction = WalletTransaction(
        wallet_id=wallet.id,
        user_id=request.user_id,
        amount=request.amount,
        transaction_type=TransactionType.CREDIT,
        created_at=datetime.utcnow(),
    )
    db.add(transaction)
    await db.commit()

    # Calculate updated balance
    balance_stmt = select(func.sum(WalletTransaction.amount)).where(WalletTransaction.wallet_id == wallet.id)
    balance_result = await db.execute(balance_stmt)
    balance = balance_result.scalar() or 0.0

    return WalletResponse(
        wallet_id=wallet.id,
        balance=balance,
        message="Wallet topped up successfully."
    )

@router.post("/wallet/pay", response_model=WalletResponse)
async def pay_from_wallet(request: WalletPaymentRequest, db: AsyncSession = Depends(get_db)) -> WalletResponse:
    """
    Deduct a specified amount from the user's wallet balance.
    """
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than zero.")

    # Fetch the user with the wallet eagerly loaded
    stmt = select(User).options(selectinload(User.wallet)).where(User.id == request.user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not user.wallet:
        raise HTTPException(status_code=404, detail="User or wallet not found.")

    wallet = user.wallet

    # Calculate current balance
    balance_stmt = select(func.sum(WalletTransaction.amount)).where(WalletTransaction.wallet_id == wallet.id)
    balance_result = await db.execute(balance_stmt)
    balance = balance_result.scalar() or 0.0

    if balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance.")

    # Add a debit transaction
    transaction = WalletTransaction(
        wallet_id=wallet.id,
        user_id=request.user_id,
        amount=-request.amount,
        transaction_type=TransactionType.DEBIT,
        created_at=datetime.utcnow(),
    )
    db.add(transaction)
    await db.commit()

    # Recalculate balance
    balance -= request.amount

    return WalletResponse(
        wallet_id=wallet.id,
        balance=balance,
        message="Payment successful."
    )

@router.get("/wallet/balance", response_model=WalletResponse)
async def check_wallet_balance(user_id: int, db: AsyncSession = Depends(get_db)) -> WalletResponse:
    """
    Retrieve the current balance of the user's wallet.
    """
    # Fetch the user with the wallet eagerly loaded
    stmt = select(User).options(selectinload(User.wallet)).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not user.wallet:
        raise HTTPException(status_code=404, detail="User or wallet not found.")

    wallet = user.wallet

    # Calculate balance
    balance_stmt = select(func.sum(WalletTransaction.amount)).where(WalletTransaction.wallet_id == wallet.id)
    balance_result = await db.execute(balance_stmt)
    balance = balance_result.scalar() or 0.0

    return WalletResponse(
        wallet_id=wallet.id,
        balance=balance,
        message="Wallet balance retrieved successfully."
    )