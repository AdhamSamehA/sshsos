### Create Cart when you choose a particular supermarket
### Add Item To Cart
### Remove Item From Cart
### Empty Cart
### View Cart (Items, Quantities, Total Price, Photo, Wallet Balance)
### Update Cart (You can remove item, edit quantities)
### 
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from schemas.cart import CreateCartRequest, CartResponse, AddItemRequest, RemoveItemRequest, UpdateCartRequest, ViewCartResponse, CartItem





######1


router = APIRouter()

@router.post("/carts/create", response_model=CartResponse)
async def create_cart(request: CreateCartRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    """
    Overview:
    Create a new cart for a particular supermarket.

    Function Logic:
    1. Accepts supermarket_id as input.
    2. Creates a new cart in the database linked to the specified supermarket.
    3. Returns the cart ID and a success message.

    Parameters:
    - request (CreateCartRequest): Contains the supermarket ID for which the cart is being created.
    - db (AsyncSession): The database session dependency for querying and inserting data.

    Returns:
    - A JSON response conforming to the CartResponse model.
    """
    # Mock response for frontend testing
    return CartResponse(
        cart_id=12345,
        supermarket_id=request.supermarket_id,
        message="Cart created successfully"
    )




#######2

@router.post("/carts/{cart_id}/add-item", response_model=CartResponse)
async def add_item_to_cart(cart_id: int, request: AddItemRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    """
    Overview:
    Add an item to the specified cart.

    Function Logic:
    1. Accepts cart_id and item details (item_id, quantity) as input.
    2. Adds the specified item to the cart in the database.
    3. Returns the updated cart details and a success message.

    Parameters:
    - cart_id (int): The ID of the cart to which the item is being added.
    - request (AddItemRequest): Contains the item ID and quantity to add.
    - db (AsyncSession): The database session dependency for querying and inserting data.

    Returns:
    - A JSON response conforming to the CartResponse model.
    """
    # Mock response for frontend testing
    return CartResponse(
        cart_id=cart_id,
        supermarket_id=1,  # Placeholder supermarket_id for mock response
        message=f"Item {request.item_id} added to cart successfully"
    )



#######3
@router.delete("/carts/{cart_id}/remove-item", response_model=CartResponse)
async def remove_item_from_cart(cart_id: int, request: RemoveItemRequest, db: AsyncSession = Depends(get_db)) -> CartResponse:
    """
    Overview:
    Remove an item from the specified cart.

    Function Logic:
    1. Accepts cart_id and item_id as input.
    2. Removes the specified item from the cart in the database.
    3. Returns the updated cart details and a success message.

    Parameters:
    - cart_id (int): The ID of the cart from which the item is being removed.
    - request (RemoveItemRequest): Contains the item ID to remove.
    - db (AsyncSession): The database session dependency for querying and deleting data.

    Returns:
    - A JSON response conforming to the CartResponse model.
    """
    # Mock response for frontend testing
    return CartResponse(
        cart_id=cart_id,
        supermarket_id=1,  # Placeholder supermarket_id for mock response
        message=f"Item {request.item_id} removed from cart successfully"
    )




#######4

@router.delete("/carts/{cart_id}/empty", response_model=CartResponse)
async def empty_cart(cart_id: int, db: AsyncSession = Depends(get_db)) -> CartResponse:
    """
    Overview:
    Empty all items from the specified cart.

    Function Logic:
    1. Accepts cart_id as input.
    2. Removes all items from the specified cart in the database.
    3. Returns a success message.

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
        cart_id=cart_id,
        supermarket_id=1,  # Placeholder supermarket_id for mock response
        message="Cart updated successfully"
    )