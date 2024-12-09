from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from server.models import Cart, Supermarket, Item, StockLevel, User, CartItems, WalletTransaction
from server.dependencies import get_db
from server.schemas import CreateCartRequest, CartResponse, AddItemRequest, RemoveItemRequest, UpdateCartRequest, ViewCartResponse, CartItem, CartItemResponse
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
    stmt = select(Cart).where(Cart.user_id == request.user_id)
    result = await db.execute(stmt)
    existing_cart = result.scalar_one_or_none()

    # Reuse or delete the existing cart if it exists
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
            # Delete the existing cart if it's for a different supermarket
            await db.delete(existing_cart)
            await db.commit()

    # Create a new cart for the user and supermarket
    new_cart = Cart(user_id=user.id, supermarket_id=supermarket.id)
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
    # Mock response for frontend testing
    return CartResponse(
        cart_id=cart_id,
        supermarket_id=1,  # Placeholder supermarket_id for mock response
        message="Cart emptied successfully"
    )




#######5

@router.put("/carts/{cart_id}/update", response_model=CartResponse)
async def update_cart(cart_id: int, request: UpdateCartRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    """
    Overview:
    Update the items in the specified cart.

    Function Logic:
    1. Accepts cart_id and updated item details (item_id, quantity) as input.
    2. Updates the specified items in the cart in the database.
    3. Returns a success message.

    Parameters:
    - cart_id (int): The ID of the cart to update.
    - request (UpdateCartRequest): Contains the updated item details (item ID and quantity).
    - db (AsyncSession): The database session dependency for querying and updating data.

    Returns:
    - A JSON response conforming to the CartResponse model.
    """
    # Mock response for frontend testing
    return CartResponse(
        cart_id=cart.id,
        supermarket_id=cart.supermarket_id,
        message="Cart emptied successfully."
    )

###### 6
@router.get("/carts/{cart_id}", response_model=ViewCartResponse)
async def view_cart(cart_id: int, db: AsyncSession = Depends(get_db)) -> ViewCartResponse:
    """
    Overview:
    View the contents of the specified cart.

    Function Logic:
    1. Accepts cart_id as input.
    2. Retrieves the cart details from the database, including items, quantities, total price, photos, and wallet balance.
    3. Returns the cart details.

    Parameters:
    - cart_id (int): The ID of the cart to view.
    - db (AsyncSession): The database session dependency for querying data.

    Returns:
    - A JSON response conforming to the ViewCartResponse model.
    """
    # Mock response for frontend testing
    return ViewCartResponse(
        cart_id=cart_id,
        items=[
            CartItem(item_id=1, name="Apple", quantity=3, price=1.5, photo_url="http://example.com/apple.jpg"),
            CartItem(item_id=2, name="Banana", quantity=2, price=1.0, photo_url="http://example.com/banana.jpg")
        ],
        total_price=6.0,
        wallet_balance=50.0
    )