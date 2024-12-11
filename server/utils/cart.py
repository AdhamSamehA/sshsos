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
from .order import get_order_slot, automated_order_placement, parse_delivery_time, aggregate_shared_cart_items, deduct_delivery_fee_contributions, add_contributor_to_shared_cart, process_payment
from sqlalchemy import select, delete
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()


import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from server.models import (
    Cart,
    CartItems,
    SharedCart,
    SharedCartContributor,
    SharedCartItem,
    Order,
    WalletTransaction,
    OrderSlot,
    Supermarket,
    Wallet,
    User
)
from server.schemas import SubmitDeliveryDetailsRequest, SubmitDeliveryDetailsResponse
from server.enums import CartStatus, SharedCartStatus, OrderStatus
from server.utils.order import parse_delivery_time, automated_order_placement, find_or_create_shared_cart

# Enumerations and Helper Functions

async def validate_cart(db: AsyncSession, cart_id: int) -> Cart:
    """
    Validates that the cart exists and is active.
    """
    result = await db.execute(
        select(Cart).where(Cart.id == cart_id, Cart.status == CartStatus.ACTIVE)
    )
    cart = result.scalars().first()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is inactive or does not exist.")
    return cart



async def transfer_cart_items_to_shared_cart(
    db: AsyncSession, normal_cart_id: int, shared_cart_id: int, user_id: int
):
    """
    Transfers items from a normal cart to a shared cart.
    """
    try:
        # Fetch all items from the normal cart
        result = await db.execute(
            select(CartItems).where(CartItems.cart_id == normal_cart_id)
        )
        cart_items = result.scalars().all()

        if not cart_items:
            print(f"No items found in the normal cart ID {normal_cart_id}.")
            raise HTTPException(status_code=400, detail="No items found in the cart.")

        #print(f"Items found in normal cart {normal_cart_id}: {[vars(item) for item in cart_items]}")

        # Verify the contributor is associated with the shared cart
        contributor_result = await db.execute(
            select(SharedCartContributor.id).where(
                SharedCartContributor.shared_cart_id == shared_cart_id,
                SharedCartContributor.user_id == user_id,
            )
        )
        contributor_id = contributor_result.scalar()
        if not contributor_id:
            print(f"User {user_id} is not associated with shared cart {shared_cart_id}.")
            raise HTTPException(
                status_code=400, detail="Contributor not associated with the shared cart."
            )

        print(f"Contributor ID for User {user_id} in Shared Cart {shared_cart_id}: {contributor_id}")

        # Transfer items to the shared cart
        for item in cart_items:
            print(f"Transferring item {item.item_id} from normal cart {normal_cart_id} to shared cart {shared_cart_id}")
            shared_cart_item = SharedCartItem(
                shared_cart_id=shared_cart_id,
                contributor_id=contributor_id,
                item_id=item.item_id,
                quantity=item.quantity,
                price=item.price,
            )
            db.add(shared_cart_item)

        # Mark the normal cart as inactive
        cart_result = await db.execute(select(Cart).where(Cart.id == normal_cart_id))
        normal_cart = cart_result.scalar_one_or_none()
        if normal_cart:
            print(f"Marking normal cart {normal_cart_id} as inactive.")
            normal_cart.status = CartStatus.INACTIVE
            db.add(normal_cart)

        await db.commit()
        print(f"Successfully transferred items from cart {normal_cart_id} to shared cart {shared_cart_id}.")

        # Fetch and print shared cart items for verification
        shared_cart_items_result = await db.execute(
            select(SharedCartItem).where(SharedCartItem.shared_cart_id == shared_cart_id)
        )
        shared_cart_items = shared_cart_items_result.scalars().all()
        print("Shared Cart Items after transfer for Shared Cart {}:".format(shared_cart_id))
        for item in shared_cart_items:
            print(f"Item ID: {item.item_id}, Quantity: {item.quantity}, Price: {item.price}, Contributor ID: {item.contributor_id}")

    except Exception as e:
        print(f"Error transferring items from normal cart {normal_cart_id} to shared cart {shared_cart_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to transfer items to shared cart: {str(e)}"
        )


async def fetch_shared_cart_items(db: AsyncSession, shared_cart_id: int):
    """
    Fetches all items in a shared cart.
    """
    result = await db.execute(
        select(SharedCartItem).where(SharedCartItem.shared_cart_id == shared_cart_id)
    )
    return result.scalars().all()

async def create_order(
    db: AsyncSession,
    shared_cart: SharedCart,
    shared_cart_items,
    user_id: int,
    address_id: int,
    order_slot_id: int,
):
    """
    Creates or updates an order for the shared cart.
    Ensures all items from all contributors are included.
    """
    try:
        for item in shared_cart_items:
            print(f"In Create Order: Item ID: {item.item_id}, Quantity: {item.quantity}, Price: {item.price}, Contributor ID: {item.contributor_id}")
        
        # Step 1: Aggregate shared cart items by item_id
        aggregated_items = await aggregate_shared_cart_items(shared_cart_items)

        # Step 2: Calculate total costs
        total_item_cost = sum(data["total_price"] for data in aggregated_items.values())
        delivery_fee = shared_cart.supermarket.delivery_fee or 0.0
        total_cost = total_item_cost + delivery_fee

        # Step 3: Fetch the existing order for the shared cart, if any
        result = await db.execute(
            select(Order).where(Order.shared_cart_id == shared_cart.id)
        )
        order = result.scalars().first()

        # Step 4: If the order exists, update it; otherwise, create a new one
        if order:
            print(f"Updating existing order ID: {order.id}")
            order.total_amount = total_cost
            order.delivery_fee = delivery_fee
            order.status = OrderStatus.SCHEDULED
        else:
            print("Creating a new order.")
            order = Order(
                user_id=user_id,
                shared_cart_id=shared_cart.id,
                supermarket_id=shared_cart.supermarket_id,
                address_id=address_id,
                delivery_fee=delivery_fee,
                total_amount=total_cost,
                order_slot_id=order_slot_id,
                status=OrderStatus.SCHEDULED,
            )
            db.add(order)
            await db.commit()  # Commit to generate an order ID

        # Step 5: Clear existing OrderItems for the order
        if order.id:
            print(f"Clearing existing order items for order ID: {order.id}")
            await db.execute(
                delete(OrderItem).where(OrderItem.order_id == order.id)
            )

        # Step 6: Add new OrderItems based on the aggregated data
        print(f"Adding items to order ID: {order.id}")
        for item_id, data in aggregated_items.items():
            order_item = OrderItem(
                order_id=order.id,
                item_id=item_id,
                quantity=data["quantity"],
                price=data["total_price"] / data["quantity"],  
            )
            db.add(order_item)

        # Step 7: Commit all changes
        await db.commit()
        print(f"Order successfully created/updated. Order ID: {order.id}")

        return order

    except Exception as e:
        print(f"Error in create_order: {e}")
        raise Exception(f"Failed to create or update order: {e}")


async def schedule_order_placement(db: AsyncSession, shared_cart_id: int, order_time: str):
    """
    Schedules automatic order placement.
    """
    environment = os.getenv("ENVIRONMENT", "production")
    if environment == "development":
        asyncio.create_task(automated_order_placement(db, shared_cart_id, delay=20))
    else:
        delivery_time = parse_delivery_time(order_time)
        current_time = datetime.utcnow()
        delay = max((delivery_time - current_time).total_seconds(), 0)
        asyncio.create_task(automated_order_placement(db, shared_cart_id, delay))

async def deactivate_cart(db: AsyncSession, cart_id: int):
    """
    Marks the cart as inactive.
    """
    result = await db.execute(select(Cart).where(Cart.id == cart_id))
    cart = result.scalar_one_or_none()
    if cart:
        cart.status = CartStatus.INACTIVE
        db.add(cart)
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
        status=OrderStatus.PLACED,
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
    Handles scheduled orders: validates the cart, manages shared cart, creates or updates order, and schedules placement.
    """
    try:
        # Step 1: Validate the cart
        cart = await validate_cart(db, cart_id)

        # Step 2: Fetch the order slot
        try:
            order_slot = await get_order_slot(request.order_time, request.supermarket_id, db)
            if not order_slot:
                raise HTTPException(status_code=400, detail=f"Invalid delivery time: {request.order_time}.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch order slot: {str(e)}")
        """
        try:
            await add_contributor_to_shared_cart(db, request.user_id, request.supermarket_id, request.address_id,order_slot.id)
        except HTTPException as http_exc:
            print(f"Error adding contributor: {http_exc.detail}")
            raise http_exc
        except Exception as e:
            print(f"Failed to add contributor: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to add contributor: {str(e)}")
        """
        try:
            shared_cart = await find_or_create_shared_cart(
                db=db,
                user_id=request.user_id,
                supermarket_id=request.supermarket_id,
                address_id=request.address_id,
                order_slot_id=order_slot.id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error finding or creating shared cart: {str(e)}")

        # Step 4: Transfer items to shared cart
        try:
            await transfer_cart_items_to_shared_cart(
                db,
                normal_cart_id=cart_id,
                shared_cart_id=shared_cart.id,
                user_id=request.user_id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to transfer items to shared cart: {str(e)}")

        # Step 5: Fetch shared cart items
        try:
            shared_cart_items = await fetch_shared_cart_items(db, shared_cart.id)
            print("Items In Shared Cart:")
            for item in shared_cart_items:
                print(f"Item ID: {item.item_id}, Quantity: {item.quantity}, Price: {item.price}, Contributor ID: {item.contributor_id}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch shared cart items: {str(e)}")

        try:
            # Fetch the shared cart with related contributors, items, and supermarket
            shared_cart_result = await db.execute(
                select(SharedCart)
                .options(
                    joinedload(SharedCart.orders),
                    joinedload(SharedCart.shared_cart_items),
                    joinedload(SharedCart.supermarket),
                    joinedload(SharedCart.contributors)
                        .joinedload(SharedCartContributor.user)
                        .joinedload(User.wallet),
                )
                .where(SharedCart.id == shared_cart.id)
            )
            shared_cart = shared_cart_result.scalars().first()
            print("Items In Shared Cart:")
            for item in shared_cart_items:
                print(f"Item ID: {item.item_id}, Quantity: {item.quantity}, Price: {item.price}, Contributor ID: {item.contributor_id}")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to find or create shared cart: {str(e)}")
        
    
        try:
            print("Items In Shared Cart:")
            for item in shared_cart_items:
                print(f"Item ID: {item.item_id}, Quantity: {item.quantity}, Price: {item.price}, Contributor ID: {item.contributor_id}")
            delivery_fee = shared_cart.supermarket.delivery_fee
            await process_payment(db, request.user_id, delivery_fee, shared_cart_items)
            print(f"Deducted max delivery fee contributions and item cost contributions for shared cart ID {shared_cart.id}.")
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Failed to deduct delivery fee contributions: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to deduct delivery fee contributions: {str(e)}")

        
        try:
            shared_cart = await find_or_create_shared_cart(
                db,
                user_id=request.user_id,
                supermarket_id=request.supermarket_id,
                address_id=request.address_id,
                order_slot_id=order_slot.id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to find or create shared cart: {str(e)}")
        
        try:
            order = await create_order(
                db=db,
                shared_cart=shared_cart,
                shared_cart_items=shared_cart_items,
                user_id=request.user_id,
                address_id=request.address_id,
                order_slot_id=order_slot.id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create or update the order: {str(e)}")

        try:
            shared_cart = await find_or_create_shared_cart(
                db,
                user_id=request.user_id,
                supermarket_id=request.supermarket_id,
                address_id=request.address_id,
                order_slot_id=order_slot.id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to find or create shared cart: {str(e)}")
        
        try:
            # Schedule automated order placement
            environment = os.getenv("ENVIRONMENT", "production")
            if environment == "development":
                asyncio.create_task(automated_order_placement(db, request.user_id, shared_cart.id, delay=20))
            else:
                delivery_time = parse_delivery_time(request.order_time)
                current_time = datetime.utcnow()
                delay = max((delivery_time - current_time).total_seconds(), 0)
                asyncio.create_task(automated_order_placement(db, request.user_id, shared_cart.id, delay=delay))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to schedule automated order placement: {str(e)}")
        #print(f"Mode: {environment}")
        #print("Scheduled Order")

        try:
            await deactivate_cart(db, cart_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to deactivate cart: {str(e)}")

        return SubmitDeliveryDetailsResponse(
            cart_id=shared_cart.id,
            delivery_time=request.order_time,
            message="Items added to the shared cart successfully. The order will be processed automatically.",
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
