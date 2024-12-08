from sqlalchemy import select, delete
from server.models import Cart, Order, Wallet
from sqlalchemy.orm import joinedload
from server.dependencies import AsyncSession


async def get_cart_by_id(db: AsyncSession, cart_id: int):
    """
    Fetch the cart by ID, including its related items.
    """
    result = await db.execute(
        select(Cart).options(joinedload(Cart.cart_items)).where(Cart.id == cart_id)
    )
    return result.scalars().first()


async def get_order_by_id(db: AsyncSession, order_id: int):
    result = await db.execute(select(Order).where(Order.id == order_id))
    return result.scalars().first()


async def get_orders_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Order).where(Order.user_id == user_id))
    return result.scalars().all()


async def get_user_wallet(db: AsyncSession, user_id: int):
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    return result.scalars().first()
