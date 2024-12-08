from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from server.models import Cart, Supermarket, Item, StockLevel, User, CartItems, WalletTransaction, OrderSlot
from server.models.carts import CartStatus
from server.dependencies import get_db
from server.utils import handle_schedule_order, handle_order_now
from server.schemas import CreateCartRequest, CartResponse, AddItemRequest, RemoveItemRequest, ViewCartResponse, CartItemResponse, SubmitDeliveryDetailsResponse, SubmitDeliveryDetailsRequest
from typing import List

######1


router = APIRouter()

@router.post("/carts/create", response_model=CartResponse)
async def create_cart(request: CreateCartRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    """
    Overview:
    Create a new cart for a particular supermarket.
    """
    # Check if the user exists
    stmt = select(User).where(User.id == request.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Check if the supermarket exists
    stmt = select(Supermarket).where(Supermarket.id == request.supermarket_id)
    result = await db.execute(stmt)
    supermarket = result.scalar_one_or_none()

    if not supermarket:
        raise HTTPException(status_code=404, detail="Supermarket not found.")

    # Check if the user already has an active cart
    stmt = select(Cart).where(Cart.user_id == request.user_id, Cart.status == CartStatus.ACTIVE).with_for_update()
    result = await db.execute(stmt)
    existing_cart = result.scalar_one_or_none()

    # Reuse or deactivate the existing cart if it exists
    if existing_cart:
        if existing_cart.supermarket_id == request.supermarket_id:
            # If the cart is for the same supermarket, reuse it
            return CartResponse(
                cart_id=existing_cart.id,
                user_id=user.id,
                supermarket_id=supermarket.id,
                message="Existing cart reused successfully."
            )
        else:
            # Mark the existing cart as inactive
            existing_cart.status = CartStatus.INACTIVE
            await db.commit()

    # Create a new active cart for the user and supermarket
    new_cart = Cart(user_id=user.id, supermarket_id=supermarket.id, status=CartStatus.ACTIVE)
    db.add(new_cart)
    await db.commit()
    await db.refresh(new_cart)

    return CartResponse(
        cart_id=new_cart.id,
        user_id=user.id,
        supermarket_id=supermarket.id,
        message="New cart created successfully."
    )

#######2

@router.post("/carts/{cart_id}/add-item", response_model=CartResponse)
async def add_item_to_cart(cart_id: int, request: AddItemRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    """
    Add an item to the specified cart.
    """
    if request.quantity < 1:
        raise HTTPException(status_code=400, detail="Requested quantity is less than 1")

     # Validate cart existence
    stmt = select(Cart).where(Cart.id == cart_id)
    result = await db.execute(stmt)
    cart = result.scalar_one_or_none()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")
    
    if cart.status != CartStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Cannot modify an inactive cart.")

    # Validate item existence
    stmt = select(Item).where(Item.id == request.item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    # Check stock levels
    stmt = select(StockLevel).with_for_update().where(
        StockLevel.item_id == request.item_id,
        StockLevel.supermarket_id == cart.supermarket_id
    )
    result = await db.execute(stmt)
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock record not found.")

    if stock.quantity < request.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock available.")

    # Reduce stock
    stock.quantity -= request.quantity

    # Add stock back to the session (optional since it's already tracked)
    db.add(stock)

    # Add item to the cart
    new_cart_item = CartItems(
        cart_id=cart_id,
        item_id=request.item_id,
        quantity=request.quantity,
        price=item.price
    )
    db.add(new_cart_item)
    await db.commit()
    await db.refresh(cart)

    return CartResponse(
        cart_id=cart.id,
        supermarket_id=cart.supermarket_id,
        message=f"Item {request.item_id} added to cart successfully"
    )


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

    # Restore stock for the removed item
    stmt = select(StockLevel).with_for_update().where(
        StockLevel.item_id == cart_item.item_id,
        StockLevel.supermarket_id == cart.supermarket_id
    )
    result = await db.execute(stmt)
    stock = result.scalar_one_or_none()

    if not stock:
        raise HTTPException(status_code=404, detail="Stock record not found for this item.")

    # Increment the stock by the quantity removed
    stock.quantity += cart_item.quantity
    db.add(stock)

    # Remove the cart item
    await db.delete(cart_item)

    # Commit changes
    await db.commit()

    # Refresh the cart object after changes
    await db.refresh(cart)

    return CartResponse(
        cart_id=cart.id,
        supermarket_id=cart.supermarket_id,
        message=f"Item {request.item_id} removed from cart successfully"
    )




#######4

@router.delete("/carts/{cart_id}/empty", response_model=CartResponse)
async def empty_cart(cart_id: int, db: AsyncSession = Depends(get_db)) -> CartResponse:
    """
    Overview:
    Empty all items from the specified cart.

    Function Logic:
    1. Validates the cart exists.
    2. Fetches all items in the specified cart.
    3. Restores the stock levels for all items in the cart.
    4. Removes all items from the cart.
    5. Returns a success message.

    Parameters:
    - cart_id (int): The ID of the cart to empty.
    - db (AsyncSession): The database session dependency for querying and deleting data.

    Returns:
    - A JSON response conforming to the CartResponse model.
    """
    # Validate the cart existence
    stmt = select(Cart).where(Cart.id == cart_id)
    result = await db.execute(stmt)
    cart = result.scalar_one_or_none()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")
    
    if cart.status != CartStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Cannot modify an inactive cart.")

    # Fetch all items in the cart
    stmt = select(CartItems).where(CartItems.cart_id == cart_id)
    result = await db.execute(stmt)
    cart_items = result.scalars().all()

    if not cart_items:
        return CartResponse(
            cart_id=cart.id,
            supermarket_id=cart.supermarket_id,
            message="Cart is already empty."
        )

    # Restore stock levels and remove all items from the cart
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

        # Delete the cart item
        await db.delete(cart_item)

    # Commit changes
    await db.commit()

    return CartResponse(
        cart_id=cart.id,
        supermarket_id=cart.supermarket_id,
        message="Cart emptied successfully."
    )


###### 5
@router.get("/carts/{cart_id}", response_model=ViewCartResponse)
async def view_cart(cart_id: int, db: AsyncSession = Depends(get_db)) -> ViewCartResponse:
    """
    View the contents of the specified cart.

    Function Logic:
    1. Validates the cart exists.
    2. Retrieves cart details, including items, their quantities, prices, and photos.
    3. Calculates the total price of the cart.
    4. Retrieves the wallet balance for the user associated with the cart.

    Parameters:
    - cart_id (int): The ID of the cart to view.
    - db (AsyncSession): The database session dependency for querying data.

    Returns:
    - A JSON response conforming to the ViewCartResponse model.
    """
    # Validate cart existence
    stmt = select(Cart).where(Cart.id == cart_id)
    result = await db.execute(stmt)
    cart = result.scalar_one_or_none()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")
    
    if cart.status != CartStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Cannot modify an inactive cart.")

    # Retrieve cart items and join with Item to get item details
    stmt = (
        select(CartItems, Item)
        .join(Item, CartItems.item_id == Item.id)
        .where(CartItems.cart_id == cart_id)
    )
    result = await db.execute(stmt)
    cart_items = result.all()

    # Process cart items
    items: List[CartItemResponse] = []
    total_price = 0.0

    for cart_item, item in cart_items:
        # Explicitly create Pydantic CartItemResponse
        item_data = {
            "item_id": item.id,
            "name": item.name,
            "quantity": cart_item.quantity,
            "price": item.price,
            "photo_url": item.photo_url,
        }
        items.append(CartItemResponse(**item_data))
        total_price += cart_item.quantity * item.price

    # Fetch wallet balance dynamically
    stmt = select(func.sum(WalletTransaction.amount)).where(WalletTransaction.user_id == cart.user_id)
    wallet_balance = (await db.execute(stmt)).scalar() or 0.0

    return ViewCartResponse(
        cart_id=cart.id,
        items=items,
        total_price=total_price,
        wallet_balance=wallet_balance
    )

####### 6
@router.post("/carts/{cart_id}/submit-delivery", response_model=SubmitDeliveryDetailsResponse)
async def submit_delivery_details(cart_id: int, request: SubmitDeliveryDetailsRequest, db: AsyncSession = Depends(get_db)) -> SubmitDeliveryDetailsResponse:
    """
    Submit delivery details and route to 'Order Now' or 'Schedule Order' logic.
    """
    if request.order_time == "now":
        # Normal cart logic
        return await handle_order_now(cart_id, request, db)
    else:
        # Validate order slot and handle shared cart logic
        return await handle_schedule_order(cart_id, request, db)


