from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime
from typing import List

from server.schemas import WalletTopUpRequest, WalletPaymentRequest, WalletResponse, WalletTransactionResponse
from server.dependencies import get_db
from server.models import Wallet, WalletTransaction, User
from server.models.wallet_transaction import TransactionType
from loguru import logger

router = APIRouter()

@router.post("/wallet/top-up", response_model=WalletResponse)
async def top_up_wallet(request: WalletTopUpRequest, db: AsyncSession = Depends(get_db)) -> WalletResponse:
    logger.info(f"Received top-up request for user_id={request.user_id}, amount={request.amount}")
    try:
        if request.amount <= 0:
            logger.warning(f"Invalid top-up amount: {request.amount}")
            raise HTTPException(status_code=400, detail="Top-up amount must be greater than zero.")

        # Fetch the user with the wallet eagerly loaded
        stmt = select(User).options(selectinload(User.wallet)).where(User.id == request.user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user or not user.wallet:
            logger.warning(f"User or wallet not found for user_id={request.user_id}")
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

        logger.info(f"Wallet topped up successfully for user_id={request.user_id}. New balance: {balance}")
        return WalletResponse(
            wallet_id=wallet.id,
            balance=balance,
            message="Wallet topped up successfully."
        )
    except HTTPException as http_exc:
        logger.error(f"HTTPException during top-up for user_id={request.user_id}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during top-up for user_id={request.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/wallet/pay", response_model=WalletResponse)
async def pay_from_wallet(request: WalletPaymentRequest, db: AsyncSession = Depends(get_db)) -> WalletResponse:
    logger.info(f"Received payment request from wallet: user_id={request.user_id}, amount={request.amount}")
    try:
        if request.amount <= 0:
            logger.warning(f"Invalid payment amount: {request.amount}")
            raise HTTPException(status_code=400, detail="Payment amount must be greater than zero.")

        # Fetch the user with the wallet eagerly loaded
        stmt = select(User).options(selectinload(User.wallet)).where(User.id == request.user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user or not user.wallet:
            logger.warning(f"User or wallet not found for user_id={request.user_id}")
            raise HTTPException(status_code=404, detail="User or wallet not found.")

        wallet = user.wallet

        # Calculate current balance
        balance_stmt = select(func.sum(WalletTransaction.amount)).where(WalletTransaction.wallet_id == wallet.id)
        balance_result = await db.execute(balance_stmt)
        balance = balance_result.scalar() or 0.0

        logger.info(f"Current balance for user_id={request.user_id} is {balance}")

        if balance < request.amount:
            logger.warning(f"Insufficient balance for user_id={request.user_id}. Requested: {request.amount}, Available: {balance}")
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
        logger.info(f"Payment successful for user_id={request.user_id}. New balance: {balance}")

        return WalletResponse(
            wallet_id=wallet.id,
            balance=balance,
            message="Payment successful."
        )
    except HTTPException as http_exc:
        logger.error(f"HTTPException during payment for user_id={request.user_id}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during payment for user_id={request.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/wallet/balance", response_model=WalletResponse)
async def check_wallet_balance(user_id: int, db: AsyncSession = Depends(get_db)) -> WalletResponse:
    logger.info(f"Fetching wallet balance for user_id={user_id}")
    try:
        # Fetch the user with the wallet eagerly loaded
        stmt = select(User).options(selectinload(User.wallet)).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user or not user.wallet:
            logger.warning(f"User or wallet not found for user_id={user_id}")
            raise HTTPException(status_code=404, detail="User or wallet not found.")

        wallet = user.wallet

        # Calculate balance
        balance_stmt = select(func.sum(WalletTransaction.amount)).where(WalletTransaction.wallet_id == wallet.id)
        balance_result = await db.execute(balance_stmt)
        balance = balance_result.scalar() or 0.0

        logger.info(f"Retrieved wallet balance for user_id={user_id}: {balance}")
        return WalletResponse(
            wallet_id=wallet.id,
            balance=balance,
            message="Wallet balance retrieved successfully."
        )
    except HTTPException as http_exc:
        logger.error(f"HTTPException while fetching balance for user_id={user_id}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching balance for user_id={user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/wallet/transactions", response_model=List[WalletTransactionResponse])
async def fetch_transaction_history(user_id: int, db: AsyncSession = Depends(get_db)) -> List[WalletTransactionResponse]:
    logger.info(f"Fetching transaction history for user_id={user_id}")
    try:
        # Fetch the user with the wallet eagerly loaded
        stmt = select(User).options(selectinload(User.wallet)).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user or not user.wallet:
            logger.warning(f"User or wallet not found for user_id={user_id}")
            raise HTTPException(status_code=404, detail="User or wallet not found.")

        wallet = user.wallet

        # Fetch transaction history
        transaction_stmt = (
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet.id)
            .order_by(WalletTransaction.created_at.desc())
        )
        transactions_result = await db.execute(transaction_stmt)
        transactions = transactions_result.scalars().all()

        logger.info(f"Fetched {len(transactions)} transactions for user_id={user_id}")
        return transactions
    except HTTPException as http_exc:
        logger.error(f"HTTPException while fetching transactions for user_id={user_id}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching transactions for user_id={user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
