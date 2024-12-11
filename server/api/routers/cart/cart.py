from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from server.models import Cart, Supermarket, Item, StockLevel, User, CartItems, WalletTransaction, OrderSlot
from server.enums import CartStatus
from server.dependencies import get_db
from server.utils import handle_schedule_order, handle_order_now
from server.schemas import CreateCartRequest, CartResponse, AddItemRequest, RemoveItemRequest, ViewCartResponse, CartItemResponse, SubmitDeliveryDetailsResponse, SubmitDeliveryDetailsRequest
from typing import List
from loguru import logger  # Add this at the top of your file


######1


router = APIRouter()

@router.post("/carts/create", response_model=CartResponse)
async def create_cart(request: CreateCartRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    logger.info(f"Create cart request received: user_id={request.user_id}, supermarket_id={request.supermarket_id}")
    try:
        # Check if the user exists
        stmt = select(User).where(User.id == request.user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"User not found: user_id={request.user_id}")
            raise HTTPException(status_code=404, detail="User not found.")

        # Check if the supermarket exists
        stmt = select(Supermarket).where(Supermarket.id == request.supermarket_id)
        result = await db.execute(stmt)
        supermarket = result.scalar_one_or_none()

        if not supermarket:
            logger.warning(f"Supermarket not found: supermarket_id={request.supermarket_id}")
            raise HTTPException(status_code=404, detail="Supermarket not found.")

        # Check if the user already has an active cart
        stmt = select(Cart).where(Cart.user_id == request.user_id, Cart.status == CartStatus.ACTIVE).with_for_update()
        result = await db.execute(stmt)
        existing_cart = result.scalar_one_or_none()

        if existing_cart:
            if existing_cart.supermarket_id == request.supermarket_id:
                logger.info(f"Reusing existing cart for user_id={request.user_id}, cart_id={existing_cart.id}")
                return CartResponse(
                    cart_id=existing_cart.id,
                    user_id=user.id,
                    supermarket_id=supermarket.id,
                    message="Existing cart reused successfully."
                )
            else:
                logger.info(f"Deactivating existing cart for user_id={request.user_id}, cart_id={existing_cart.id}")
                existing_cart.status = CartStatus.INACTIVE
                await db.commit()

        # Create a new active cart for the user and supermarket
        new_cart = Cart(user_id=user.id, supermarket_id=supermarket.id, status=CartStatus.ACTIVE)
        db.add(new_cart)
        await db.commit()
        await db.refresh(new_cart)

        logger.info(f"New cart created: cart_id={new_cart.id}, user_id={user.id}, supermarket_id={supermarket.id}")
        return CartResponse(
            cart_id=new_cart.id,
            user_id=user.id,
            supermarket_id=supermarket.id,
            message="New cart created successfully."
        )
    except Exception as e:
        logger.error(f"Error creating cart for user_id={request.user_id}, supermarket_id={request.supermarket_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/carts/{cart_id}/add-item", response_model=CartResponse)
async def add_item_to_cart(cart_id: int, request: AddItemRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    logger.info(f"Add item request: cart_id={cart_id}, item_id={request.item_id}, quantity={request.quantity}")
    try:
        if request.quantity < 1:
            logger.warning(f"Invalid quantity for item: item_id={request.item_id}, quantity={request.quantity}")
            raise HTTPException(status_code=400, detail="Requested quantity is less than 1")

        # Validate cart existence
        stmt = select(Cart).where(Cart.id == cart_id)
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart:
            logger.error(f"Cart not found: cart_id={cart_id}")
            raise HTTPException(status_code=404, detail="Cart not found.")
        
        if cart.status != CartStatus.ACTIVE:
            logger.warning(f"Inactive cart modification attempt: cart_id={cart_id}")
            raise HTTPException(status_code=400, detail="Cannot modify an inactive cart.")

        # Validate item existence
        stmt = select(Item).where(Item.id == request.item_id)
        result = await db.execute(stmt)
        item = result.scalar_one_or_none()

        if not item:
            logger.error(f"Item not found: item_id={request.item_id}")
            raise HTTPException(status_code=404, detail="Item not found.")

        # Check stock levels
        stmt = select(StockLevel).with_for_update().where(
            StockLevel.item_id == request.item_id,
            StockLevel.supermarket_id == cart.supermarket_id
        )
        result = await db.execute(stmt)
        stock = result.scalar_one_or_none()

        if not stock:
            logger.error(f"Stock record not found: item_id={request.item_id}, supermarket_id={cart.supermarket_id}")
            raise HTTPException(status_code=404, detail="Stock record not found.")

        if stock.quantity < request.quantity:
            logger.warning(f"Insufficient stock: item_id={request.item_id}, requested={request.quantity}, available={stock.quantity}")
            raise HTTPException(status_code=400, detail="Insufficient stock available.")

        # Check if the item is already in the cart
        stmt = select(CartItems).where(CartItems.cart_id == cart_id, CartItems.item_id == request.item_id)
        result = await db.execute(stmt)
        existing_cart_item = result.scalar_one_or_none()

        if existing_cart_item:
            existing_cart_item.quantity += request.quantity
            existing_cart_item.price = item.price
            logger.info(f"Updated item quantity in cart: cart_id={cart_id}, item_id={request.item_id}, new_quantity={existing_cart_item.quantity}")
        else:
            new_cart_item = CartItems(
                cart_id=cart_id,
                item_id=request.item_id,
                quantity=request.quantity,
                price=item.price
            )
            db.add(new_cart_item)
            logger.info(f"Added new item to cart: cart_id={cart_id}, item_id={request.item_id}, quantity={request.quantity}")

        # Reduce stock
        stock.quantity -= request.quantity
        db.add(stock)
        logger.info(f"Stock updated: item_id={request.item_id}, remaining_stock={stock.quantity}")

        await db.commit()
        await db.refresh(cart)

        logger.info(f"Item successfully added to cart: cart_id={cart_id}, item_id={request.item_id}")
        return CartResponse(
            cart_id=cart.id,
            supermarket_id=cart.supermarket_id,
            message=f"Item {request.item_id} added to cart successfully"
        )
    except Exception as e:
        logger.error(f"Error adding item to cart: cart_id={cart_id}, item_id={request.item_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


#######3
@router.delete("/carts/{cart_id}/remove-item", response_model=CartResponse)
async def remove_item_from_cart(cart_id: int, request: RemoveItemRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    # Validate the cart existence
    stmt = select(Cart).where(Cart.id == cart_id)
    result = await db.execute(stmt)
    cart = result.scalar_one_or_none()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")
    
    if cart.status != CartStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Cannot modify an inactive cart.")

    # Validate that the item exists in the cart
    stmt = select(CartItems).where(
        CartItems.cart_id == cart_id,
        CartItems.item_id == request.item_id
    )
    result = await db.execute(stmt)
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in the cart.")

    # Restore stock for the removed quantity
    stmt = select(StockLevel).with_for_update().where(
        StockLevel.item_id == cart_item.item_id,
        StockLevel.supermarket_id == cart.supermarket_id
    )
    result = await db.execute(stmt)
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock record not found for this item.")

    # Decrease the item's quantity or remove it if the quantity is 1
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        stock.quantity += 1  # Restore 1 unit to stock
        db.add(cart_item)  # Update cart item
    else:
        stock.quantity += cart_item.quantity  # Restore full quantity to stock
        await db.delete(cart_item)  # Remove the item entirely

    db.add(stock)  # Update stock
    await db.commit()
    await db.refresh(cart)

    return CartResponse(
        cart_id=cart.id,
        supermarket_id=cart.supermarket_id,
        message=f"One quantity of item {request.item_id} removed from cart successfully"
    )





#######4
@router.delete("/carts/{cart_id}/remove-item", response_model=CartResponse)
async def remove_item_from_cart(cart_id: int, request: RemoveItemRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    logger.info(f"Remove item request received: cart_id={cart_id}, item_id={request.item_id}")
    try:
        # Validate the cart existence
        stmt = select(Cart).where(Cart.id == cart_id)
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart:
            logger.warning(f"Cart not found: cart_id={cart_id}")
            raise HTTPException(status_code=404, detail="Cart not found.")
        
        if cart.status != CartStatus.ACTIVE:
            logger.warning(f"Cannot modify inactive cart: cart_id={cart_id}")
            raise HTTPException(status_code=400, detail="Cannot modify an inactive cart.")

        # Validate that the item exists in the cart
        stmt = select(CartItems).where(
            CartItems.cart_id == cart_id,
            CartItems.item_id == request.item_id
        )
        result = await db.execute(stmt)
        cart_item = result.scalar_one_or_none()

        if not cart_item:
            logger.warning(f"Item not found in cart: cart_id={cart_id}, item_id={request.item_id}")
            raise HTTPException(status_code=404, detail="Item not found in the cart.")

        # Restore stock for the removed quantity
        stmt = select(StockLevel).with_for_update().where(
            StockLevel.item_id == cart_item.item_id,
            StockLevel.supermarket_id == cart.supermarket_id
        )
        result = await db.execute(stmt)
        stock = result.scalar_one_or_none()

        if not stock:
            logger.warning(f"Stock record not found: item_id={cart_item.item_id}, supermarket_id={cart.supermarket_id}")
            raise HTTPException(status_code=404, detail="Stock record not found for this item.")

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            stock.quantity += 1
            db.add(cart_item)
            logger.info(f"Decreased item quantity: cart_id={cart_id}, item_id={request.item_id}, remaining_quantity={cart_item.quantity}")
        else:
            stock.quantity += cart_item.quantity
            await db.delete(cart_item)
            logger.info(f"Removed item from cart: cart_id={cart_id}, item_id={request.item_id}")

        db.add(stock)
        await db.commit()
        await db.refresh(cart)

        logger.info(f"Item successfully removed from cart: cart_id={cart_id}, item_id={request.item_id}")
        return CartResponse(
            cart_id=cart.id,
            supermarket_id=cart.supermarket_id,
            message=f"One quantity of item {request.item_id} removed from cart successfully"
        )
    except Exception as e:
        logger.error(f"Error removing item from cart: cart_id={cart_id}, item_id={request.item_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/carts/{cart_id}/empty", response_model=CartResponse)
async def empty_cart(cart_id: int, db: AsyncSession = Depends(get_db)) -> CartResponse:
    logger.info(f"Empty cart request received: cart_id={cart_id}")
    try:
        # Validate the cart existence
        stmt = select(Cart).where(Cart.id == cart_id)
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart:
            logger.warning(f"Cart not found: cart_id={cart_id}")
            raise HTTPException(status_code=404, detail="Cart not found.")
        
        if cart.status != CartStatus.ACTIVE:
            logger.warning(f"Cannot modify inactive cart: cart_id={cart_id}")
            raise HTTPException(status_code=400, detail="Cannot modify an inactive cart.")

        # Fetch all items in the cart
        stmt = select(CartItems).where(CartItems.cart_id == cart_id)
        result = await db.execute(stmt)
        cart_items = result.scalars().all()

        if not cart_items:
            logger.info(f"Cart already empty: cart_id={cart_id}")
            return CartResponse(
                cart_id=cart.id,
                supermarket_id=cart.supermarket_id,
                message="Cart is already empty."
            )

        # Restore stock levels and remove all items
        for cart_item in cart_items:
            stmt = select(StockLevel).with_for_update().where(
                StockLevel.item_id == cart_item.item_id,
                StockLevel.supermarket_id == cart.supermarket_id
            )
            result = await db.execute(stmt)
            stock = result.scalar_one_or_none()

            if stock:
                stock.quantity += cart_item.quantity
                db.add(stock)
                logger.info(f"Restored stock: item_id={cart_item.item_id}, restored_quantity={cart_item.quantity}")

            await db.delete(cart_item)

        await db.commit()
        logger.info(f"Cart emptied successfully: cart_id={cart_id}")
        return CartResponse(
            cart_id=cart.id,
            supermarket_id=cart.supermarket_id,
            message="Cart emptied successfully."
        )
    except Exception as e:
        logger.error(f"Error emptying cart: cart_id={cart_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/carts/{cart_id}", response_model=ViewCartResponse)
async def view_cart(cart_id: int, db: AsyncSession = Depends(get_db)) -> ViewCartResponse:
    logger.info(f"View cart request received: cart_id={cart_id}")
    try:
        stmt = select(Cart).where(Cart.id == cart_id)
        result = await db.execute(stmt)
        cart = result.scalar_one_or_none()

        if not cart:
            logger.warning(f"Cart not found: cart_id={cart_id}")
            raise HTTPException(status_code=404, detail="Cart not found.")
        
        if cart.status != CartStatus.ACTIVE:
            logger.warning(f"Cannot view inactive cart: cart_id={cart_id}")
            raise HTTPException(status_code=400, detail="Cannot modify an inactive cart.")

        stmt = (
            select(CartItems, Item)
            .join(Item, CartItems.item_id == Item.id)
            .where(CartItems.cart_id == cart_id)
        )
        result = await db.execute(stmt)
        cart_items = result.all()

        items: List[CartItemResponse] = []
        total_price = 0.0

        for cart_item, item in cart_items:
            items.append(CartItemResponse(
                item_id=item.id,
                name=item.name,
                quantity=cart_item.quantity,
                price=item.price,
                photo_url=item.photo_url,
            ))
            total_price += cart_item.quantity * item.price

        stmt = select(func.sum(WalletTransaction.amount)).where(WalletTransaction.user_id == cart.user_id)
        wallet_balance = (await db.execute(stmt)).scalar() or 0.0

        logger.info(f"Cart viewed successfully: cart_id={cart_id}, total_price={total_price}, wallet_balance={wallet_balance}")
        return ViewCartResponse(
            cart_id=cart.id,
            items=items,
            total_price=total_price,
            wallet_balance=wallet_balance
        )
    except Exception as e:
        logger.error(f"Error viewing cart: cart_id={cart_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/carts/{cart_id}/submit-delivery", response_model=SubmitDeliveryDetailsResponse)
async def submit_delivery_details(cart_id: int, request: SubmitDeliveryDetailsRequest, db: AsyncSession = Depends(get_db)) -> SubmitDeliveryDetailsResponse:
    logger.info(f"Submit delivery details request received: cart_id={cart_id}, order_time={request.order_time}")
    try:
        if request.order_time == "now":
            return await handle_order_now(cart_id, request, db)
        else:
            return await handle_schedule_order(cart_id, request, db)
    except Exception as e:
        logger.error(f"Error submitting delivery details: cart_id={cart_id}, order_time={request.order_time}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
