from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from server.dependencies import AsyncSession
from server.schemas import SubmitDeliveryDetailsRequest, SubmitDeliveryDetailsResponse
from server.models import SharedCart, CartItems, SharedCartItem, Order, OrderSlot, Supermarket, Wallet, WalletTransaction, SharedCartContributor, OrderItem, Cart
from server.models.shared_cart import SharedCartStatus
from server.models.order import OrderStatus
from server.models.carts import CartStatus
from server.models.wallet_transaction import TransactionType
from .user import get_cart_by_id
from .order import get_order_slot, automated_order_placement, parse_delivery_time
from sqlalchemy import select, delete
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()


async def find_or_create_shared_cart(
    db: AsyncSession,
    user_id: int,
    supermarket_id: int,
    address_id: int,
    order_slot_id: int
) -> SharedCart:
    """
    Find or create a shared cart with the specified parameters.
    Ensures that the user is a contributor to the shared cart.
    """
    try:
        # Find existing shared cart
        result = await db.execute(
            select(SharedCart)
            .where(
                SharedCart.supermarket_id == supermarket_id,
                SharedCart.address_id == address_id,
                SharedCart.order_slot_id == order_slot_id,
                SharedCart.status == SharedCartStatus.OPEN,
            )
        )
        shared_cart = result.scalars().first()
        print("Found Existing Shared Cart")

        if not shared_cart:
            # Create new shared cart
            shared_cart = SharedCart(
                supermarket_id=supermarket_id,
                address_id=address_id,
                order_slot_id=order_slot_id,
                status=SharedCartStatus.OPEN,
            )
            db.add(shared_cart)
            await db.commit()
            await db.refresh(shared_cart)
            #logger.info(f"Created new shared cart with ID {shared_cart.id}")

        # Check if the user is already a contributor
        contributor_result = await db.execute(
            select(SharedCartContributor)
            .where(
                SharedCartContributor.shared_cart_id == shared_cart.id,
                SharedCartContributor.user_id == user_id
            )
        )
        contributor = contributor_result.scalars().first()

        if not contributor:
            # Calculate initial delivery_fee_contribution
            # For initial contributors, each pays the maximum delivery fee
            # This value can be updated later when the order is placed
            # Assuming you have access to Supermarket.delivery_fee
            supermarket_result = await db.execute(
                select(Supermarket.delivery_fee)
                .where(Supermarket.id == supermarket_id)
            )
            delivery_fee = supermarket_result.scalar()
            if delivery_fee is None:
                raise HTTPException(status_code=400, detail="Supermarket delivery fee not set.")

            contributor = SharedCartContributor(
                shared_cart_id=shared_cart.id,
                user_id=user_id,
                delivery_fee_contribution=delivery_fee  # Initially, each contributor pays the max fee
                # wallet_transaction_id can be set here if available, else left as None
            )
            db.add(contributor)
            await db.commit()
            await db.refresh(contributor)
            #logger.info(f"Added user {user_id} as contributor to shared cart {shared_cart.id}")

        return shared_cart

    except Exception as e:
        #logger.exception("Error in find_or_create_shared_cart")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def transfer_cart_items_to_shared_cart(
    db: AsyncSession, 
    normal_cart_id: int, 
    shared_cart_id: int,
    user_id: int  
):
    """
    Transfer items from a normal cart to a shared cart.
    """
    # Eagerly load 'cart' relationship to prevent lazy loading
    result = await db.execute(
        select(CartItems)
        .options(joinedload(CartItems.cart))  
        .where(CartItems.cart_id == normal_cart_id)
    )
    cart_items = result.scalars().all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="No items found in the cart.")

    # Fetch the SharedCartContributor.id for the user and shared_cart
    contributor_result = await db.execute(
        select(SharedCartContributor.id)
        .where(
            SharedCartContributor.shared_cart_id == shared_cart_id,
            SharedCartContributor.user_id == user_id
        )
    )
    contributor_id = contributor_result.scalar()

    if not contributor_id:
        raise HTTPException(
            status_code=400, 
            detail="Contributor not associated with the shared cart."
        )

    for item in cart_items:
        # Ensure 'cart' is loaded
        if not item.cart:
            raise HTTPException(status_code=400, detail="Associated cart not found for an item.")

        # Add item to shared cart
        shared_cart_item = SharedCartItem(
            shared_cart_id=shared_cart_id,      
            contributor_id=contributor_id,      
            item_id=item.item_id,
            quantity=item.quantity,
            price=item.price
        )
        db.add(shared_cart_item)

    # Clear items from the normal cart
    #await db.execute(delete(CartItems).where(CartItems.cart_id == normal_cart_id))
    # Mark the normal cart as inactive
    cart_result = await db.execute(select(Cart).where(Cart.id == normal_cart_id))
    normal_cart = cart_result.scalar_one_or_none()
    if normal_cart:
        normal_cart.status = CartStatus.INACTIVE
        db.add(normal_cart)

    await db.commit()


async def handle_order_now(cart_id: int, request: SubmitDeliveryDetailsRequest, db: AsyncSession) -> SubmitDeliveryDetailsResponse:
    """
    Handle 'Order Now' logic: place order and deduct wallet balance.
    """
    print(f"Checking for existing orders for cart_id: {cart_id}")
    existing_order = await db.execute(
        select(Order).where(Order.cart_id == cart_id, Order.status != OrderStatus.CANCELED)
    )
    if existing_order.scalars().first():
        print(f"Order already exists for cart_id: {cart_id}")
        raise HTTPException(status_code=400, detail="An order has already been placed for this cart.")
    
    print(f"Fetching cart for cart_id: {cart_id}")
    cart = await get_cart_by_id(db, cart_id)
    if not cart:
        print(f"Cart not found for cart_id: {cart_id}")
        raise HTTPException(status_code=404, detail="Cart not found")
    
    if cart.status != CartStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Cart is no longer active.")

    if not cart.cart_items:
        print(f"Cart {cart_id} is empty")
        raise HTTPException(status_code=400, detail="Cart is empty")


    print(f"Fetching supermarket details for supermarket_id: {cart.supermarket_id}")
    supermarket = await db.execute(
        select(Supermarket).where(Supermarket.id == cart.supermarket_id)
    )
    supermarket = supermarket.scalars().first()

    if not supermarket:
        print(f"Supermarket not found for supermarket_id: {cart.supermarket_id}")
        raise HTTPException(status_code=404, detail="Supermarket not found")

    total_item_cost = sum(item.quantity * item.price for item in cart.cart_items)
    delivery_fee = supermarket.delivery_fee or 0.0
    total_cost = total_item_cost + delivery_fee
    print(f"Total item cost: {total_item_cost}, Delivery fee: {delivery_fee}, Total cost: {total_cost}")

    print(f"Fetching wallet for user_id: {cart.user_id}")
    wallet = await db.execute(
        select(Wallet).where(Wallet.user_id == cart.user_id)
    )
    wallet = wallet.scalars().first()

    if not wallet:
        print(f"Wallet not found for user_id: {cart.user_id}")
        raise HTTPException(status_code=404, detail="Wallet not found")

    print(f"Calculating wallet balance for wallet_id: {wallet.id}")
    balance_result = await db.execute(
        select(func.sum(WalletTransaction.amount)).where(WalletTransaction.wallet_id == wallet.id)
    )
    balance = balance_result.scalar() or 0.0
    print(f"Current wallet balance: {balance}")

    if balance < total_cost:
        print(f"Insufficient wallet balance for user_id: {cart.user_id}. Required: {total_cost}, Available: {balance}")
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    wallet_transaction = WalletTransaction(
        wallet_id=wallet.id,
        user_id=cart.user_id,
        amount=-total_cost,
        transaction_type=TransactionType.DEBIT,
        created_at=datetime.utcnow(),
    )
    db.add(wallet_transaction)

    print(f"Creating order slot for supermarket_id: {cart.supermarket_id}")
    now_slot = await get_order_slot("now", cart.supermarket_id, db)

    print(f"Creating order for cart_id: {cart.id}")
    order = Order(
        user_id=cart.user_id,
        supermarket_id=cart.supermarket_id,
        address_id=request.address_id,
        delivery_fee=delivery_fee,
        total_amount=total_cost,
        cart_id=cart.id,
        status=OrderStatus.COMPLETED,
        order_slot_id=now_slot.id,
    )
    db.add(order)
    await db.flush()

     # Create OrderItem entries from CartItems
    print(f"Transferring items from cart_id: {cart_id} to order_id: {order.id}")
    for cart_item in cart.cart_items:
        order_item = OrderItem(
            order_id=order.id,
            item_id=cart_item.item_id,
            quantity=cart_item.quantity,
            price=cart_item.price,
        )
        db.add(order_item)

    cart.status = CartStatus.INACTIVE
    await db.commit()
    await db.refresh(order)

    print(f"Order placed successfully for cart_id: {cart.id}")
    return SubmitDeliveryDetailsResponse(
        cart_id=cart.id,
        delivery_time="now",
        message="Order placed successfully. Cart has been marked as inactive.",
    )


async def handle_schedule_order(cart_id: int, request: SubmitDeliveryDetailsRequest, db: AsyncSession) -> SubmitDeliveryDetailsResponse:
    """
    Handle 'Schedule Order' logic: manage shared carts and trigger automated order placement.
    """
    # Check if the cart is active
    cart_result = await db.execute(
        select(Cart).where(Cart.id == cart_id, Cart.status == CartStatus.ACTIVE)
    )
    cart = cart_result.scalars().first()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is inactive or does not exist.")

    # Check if an order has already been placed for this cart_id
    existing_order_result = await db.execute(
        select(Order).where(Order.cart_id == cart_id, Order.status != OrderStatus.CANCELED)
    )
    existing_order = existing_order_result.scalars().first()
    if existing_order:
        raise HTTPException(status_code=400, detail="An order has already been placed for this cart.")

    # Check if an order has been placed for a shared cart associated with this cart
    shared_cart_result = await db.execute(
        select(SharedCart.id).join(SharedCartContributor)
        .where(SharedCartContributor.user_id == cart.user_id)
    )
    shared_cart_id = shared_cart_result.scalars().first()

    if shared_cart_id:
        shared_cart_order_result = await db.execute(
            select(Order).where(Order.shared_cart_id == shared_cart_id, Order.status != OrderStatus.CANCELED)
        )
        shared_cart_order = shared_cart_order_result.scalars().first()
        if shared_cart_order:
            raise HTTPException(status_code=400, detail="An order has already been placed for the associated shared cart.")

    # Fetch the order slot
    order_slot = await get_order_slot(request.order_time, request.supermarket_id, db)
    if not order_slot:
        raise HTTPException(status_code=400, detail=f"Invalid delivery time: {request.order_time}.")

    # Find or create a shared cart
    shared_cart = await find_or_create_shared_cart(
        db,
        user_id=request.user_id,
        supermarket_id=request.supermarket_id,
        address_id=request.address_id,
        order_slot_id=order_slot.id,
    )

    # Transfer items to the shared cart
    await transfer_cart_items_to_shared_cart(
        db,
        cart_id,
        shared_cart.id,
        request.user_id,
    )

    # Schedule automated order placement
    environment = os.getenv("ENVIRONMENT", "production")
    if environment == "development":
        asyncio.create_task(automated_order_placement(db, shared_cart.id, delay=20))
    else:
        delivery_time = parse_delivery_time(request.order_time)
        current_time = datetime.utcnow()
        delay = max((delivery_time - current_time).total_seconds(), 0)
        asyncio.create_task(automated_order_placement(db, shared_cart.id, delay=delay))

    # Mark the cart as inactive to prevent further orders
    cart.status = CartStatus.INACTIVE
    db.add(cart)
    await db.commit()

    return SubmitDeliveryDetailsResponse(
        cart_id=shared_cart.id,
        delivery_time=f"Scheduled at {request.order_time}",
        message="Items added to the shared cart successfully. The order will be processed automatically.",
    )