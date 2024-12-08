from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import defaultdict
import asyncio

from server.models import (
    SharedCart,
    Wallet,
    Supermarket,
    Order,
    OrderSlot,
    SharedCartContributor,
    WalletTransaction,
    OrderItem,
)
from server.models.shared_cart import SharedCartStatus
from server.models.order import OrderStatus
from server.models.wallet_transaction import TransactionType


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
    await asyncio.sleep(delay)

    try:
        shared_cart_result = await db.execute(
            select(SharedCart)
            .options(
                joinedload(SharedCart.contributors).joinedload(SharedCartContributor.user),
                joinedload(SharedCart.shared_cart_items),
                joinedload(SharedCart.supermarket),
            )
            .where(SharedCart.id == shared_cart_id)
        )
        shared_cart = shared_cart_result.scalars().first()
        if not shared_cart:
            raise HTTPException(status_code=400, detail="Shared cart not found.")

        delivery_fee = shared_cart.supermarket.delivery_fee
        if delivery_fee is None:
            raise HTTPException(status_code=400, detail="Supermarket delivery fee not set.")

        contributors = shared_cart.contributors
        if not contributors:
            raise HTTPException(status_code=400, detail="No contributors found in the shared cart.")

        await update_delivery_fee_contribution(db, shared_cart)

        total_item_cost = sum(
            item.price * item.quantity for item in shared_cart.shared_cart_items
        )

        existing_order_result = await db.execute(
        select(Order).where(Order.shared_cart_id == shared_cart.id, Order.status != OrderStatus.CANCELED)
        )
        existing_order = existing_order_result.scalars().first()
        if existing_order:
            raise HTTPException(status_code=400, detail="An order has already been placed for this shared cart.")
        
        # Aggregate items by item_id
        aggregated_items = await aggregate_shared_cart_items(shared_cart.shared_cart_items)

        # Calculate total item costs
        total_item_cost = sum(data["total_price"] for data in aggregated_items.values())

        order = await create_order(
            db=db,
            user_id=contributors[0].user_id,  # First contributor as organizer
            supermarket_id=shared_cart.supermarket_id,
            address_id=shared_cart.address_id,
            delivery_fee=delivery_fee,
            total_amount=total_item_cost + delivery_fee,
            shared_cart_id=shared_cart.id,
            order_slot_id=shared_cart.order_slot_id,
            status=OrderStatus.COMPLETED,
        )

        # Add aggregated items to the order
        for item_id, data in aggregated_items.items():
            order_item = OrderItem(
                order_id=order.id,
                item_id=item_id,
                quantity=data["quantity"],
                price=data["total_price"] / data["quantity"], 
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


async def update_delivery_fee_contribution(db: AsyncSession, shared_cart: SharedCart):
    """
    Update delivery_fee_contribution for all contributors in the shared cart.
    """
    delivery_fee = shared_cart.supermarket.delivery_fee or 0.0
    contributors = shared_cart.contributors
    num_contributors = len(contributors)

    if num_contributors == 0:
        raise HTTPException(status_code=400, detail="No contributors found.")

    new_contribution = delivery_fee / num_contributors

    for contributor in contributors:
        user = contributor.user
        wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
        wallet = wallet_result.scalars().first()

        if not wallet:
            raise HTTPException(status_code=400, detail=f"Wallet not found for user_id {user.id}.")

        refund_amount = contributor.delivery_fee_contribution - new_contribution
        contributor.delivery_fee_contribution = new_contribution

        if refund_amount > 0:
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


async def aggregate_shared_cart_items(shared_cart_items):
    """
    Aggregate items from the shared cart by item_id.
    """
    aggregated_items = defaultdict(lambda: {"quantity": 0, "total_price": 0.0})

    for shared_cart_item in shared_cart_items:
        item_id = shared_cart_item.item_id
        aggregated_items[item_id]["quantity"] += shared_cart_item.quantity
        aggregated_items[item_id]["total_price"] += shared_cart_item.quantity * shared_cart_item.price

    return aggregated_items



async def get_order_slot(slot : str, supermarket_id : int, db: AsyncSession) -> OrderSlot:
    """
    Fetch the 'now' order slot
    """
    result = await db.execute(
        select(OrderSlot).where(OrderSlot.delivery_time == slot, OrderSlot.supermarket_id == supermarket_id)
    )
    now_slot = result.scalars().first()

    return now_slot
