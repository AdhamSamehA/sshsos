from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from datetime import datetime
from server.dependencies import AsyncSession
from server.models import SharedCart, Wallet, Supermarket, Order, OrderSlot, SharedCartContributor, WalletTransaction, OrderItem
from server.models.shared_cart import SharedCartStatus
from server.models.order import OrderStatus
from server.models.wallet_transaction import TransactionType
from sqlalchemy import select
import asyncio


def parse_delivery_time(delivery_time: str) -> datetime:
    """
    Parse the delivery time string (e.g., "6:00AM") into a datetime object for today.
    """
    current_date = datetime.utcnow().date()
    return datetime.strptime(f"{current_date} {delivery_time}", "%Y-%m-%d %I:%M%p")


async def automated_order_placement(db: AsyncSession, shared_cart_id: int, delay: int):
    """
    Automatically place the order for the shared cart after the specified delay.
    Includes refund logic for delivery fee adjustments.
    """
    # Wait for the delay
    await asyncio.sleep(delay)

    try:
        # Fetch the shared cart and related data
        shared_cart_result = await db.execute(
            select(SharedCart)
            .options(
                joinedload(SharedCart.contributors),
                joinedload(SharedCart.shared_cart_items),
                joinedload(SharedCart.supermarket),  # Load supermarket relationship
            )
            .where(SharedCart.id == shared_cart_id)
        )
        shared_cart = shared_cart_result.scalars().first()
        if not shared_cart:
            raise HTTPException(status_code=400, detail="Shared cart not found.")

        # Fetch delivery fee
        delivery_fee = shared_cart.supermarket.delivery_fee
        if delivery_fee is None:
            raise HTTPException(status_code=400, detail="Supermarket delivery fee not set.")

        # Fetch contributors
        contributors_result = await db.execute(
            select(SharedCartContributor)
            .where(SharedCartContributor.shared_cart_id == shared_cart_id)
        )
        contributors = contributors_result.scalars().all()
        if not contributors:
            raise HTTPException(status_code=400, detail="No contributors found in the shared cart.")

        # Use the first contributor as the organizer
        organizer = contributors[0]  # Assumes the first contributor is the organizer

        # Update delivery fee contributions and handle refunds
        await update_delivery_fee_contribution(db, shared_cart_id)

        # Calculate total item costs
        total_item_cost = sum(
            item.price * item.quantity for item in shared_cart.shared_cart_items
        )

        # Create the shared order
        order = await create_order(
            db=db,
            user_id=organizer.user_id,  # Use the organizer's user ID
            supermarket_id=shared_cart.supermarket_id,
            address_id=shared_cart.address_id,
            delivery_fee=delivery_fee,
            total_amount=total_item_cost + delivery_fee,
            shared_cart_id=shared_cart.id,
            order_slot_id=shared_cart.order_slot_id,
            status=OrderStatus.COMPLETED,
        )
        
        for shared_cart_item in shared_cart.shared_cart_items:
            order_item = OrderItem(
                order_id=order.id,
                item_id=shared_cart_item.item_id,
                quantity=shared_cart_item.quantity,
                price=shared_cart_item.price,
            )
            db.add(order_item)

        # Update shared cart status to CLOSED
        shared_cart.status = SharedCartStatus.CLOSED
        await db.commit()

        return order

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
    

async def create_order(
    db: AsyncSession,
    user_id: int,
    supermarket_id: int,
    address_id: int,
    delivery_fee: float,
    total_amount: float,
    cart_id: int = None,
    shared_cart_id: int = None,
    order_slot_id: int = None,
    status: OrderStatus = OrderStatus.PENDING,
):
    """
    Create an order in the database for individual or shared cart scenarios.
    """
    order = Order(
        user_id=user_id,
        supermarket_id=supermarket_id,
        address_id=address_id,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        cart_id=cart_id,
        shared_cart_id=shared_cart_id,
        order_slot_id=order_slot_id,
        status=status,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def get_order_slot(slot : str, supermarket_id : int, db: AsyncSession) -> OrderSlot:
    """
    Fetch the 'now' order slot
    """
    result = await db.execute(
        select(OrderSlot).where(OrderSlot.delivery_time == slot, OrderSlot.supermarket_id == supermarket_id)
    )
    now_slot = result.scalars().first()

    return now_slot


async def update_delivery_fee_contribution(db: AsyncSession, shared_cart_id: int):
    """
    Update delivery_fee_contribution for all contributors in the shared cart.
    The delivery fee is divided equally among all contributors.
    Includes refund logic for overpayments.
    """
    try:
        # Fetch shared cart with contributors and supermarket
        shared_cart_result = await db.execute(
            select(SharedCart)
            .options(
                joinedload(SharedCart.supermarket),
                joinedload(SharedCart.contributors).joinedload(SharedCartContributor.user),
            )
            .where(SharedCart.id == shared_cart_id)
        )
        shared_cart = shared_cart_result.scalars().first()
        if not shared_cart:
            raise HTTPException(status_code=400, detail="Shared cart not found.")

        # Fetch the delivery fee from the supermarket
        delivery_fee = shared_cart.supermarket.delivery_fee
        if delivery_fee is None:
            raise HTTPException(status_code=400, detail="Supermarket delivery fee not set.")

        # Get the contributors
        contributors = shared_cart.contributors
        num_contributors = len(contributors)
        if num_contributors == 0:
            raise HTTPException(status_code=400, detail="No contributors found in the shared cart.")

        # Calculate the new delivery_fee_contribution
        new_contribution = delivery_fee / num_contributors

        # Update contributors and issue refunds if necessary
        for contributor in contributors:
            user = contributor.user  # Fetch the related User object
            if not user:
                raise HTTPException(status_code=400, detail="Contributor user record not found.")

            # Fetch the wallet for the contributor
            wallet_result = await db.execute(
                select(Wallet).where(Wallet.user_id == user.id)
            )
            wallet = wallet_result.scalars().first()
            if not wallet:
                raise HTTPException(
                    status_code=400,
                    detail=f"Wallet not found for user_id {user.id}."
                )

            previous_contribution = contributor.delivery_fee_contribution
            contributor.delivery_fee_contribution = new_contribution
            refund_amount = previous_contribution - new_contribution

            if refund_amount > 0:
                # Issue refund via wallet transaction
                refund_transaction = WalletTransaction(
                    wallet_id=wallet.id,
                    user_id=user.id,
                    amount=refund_amount,
                    transaction_type=TransactionType.CREDIT,
                    created_at=datetime.utcnow(),
                )
                db.add(refund_transaction)

            db.add(contributor)

        await db.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
