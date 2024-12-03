from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from server.dependencies import get_db
from server.schemas import SubmitDeliveryDetailsRequest, SubmitDeliveryDetailsResponse, PaymentSummaryResponse, CancelOrderResponse, TrackOrderResponse, OrderSlotsResponse, AddressesResponse, Address, CartItem


router = APIRouter()

@router.post("/orders/{order_id}/submit-delivery", response_model=SubmitDeliveryDetailsResponse)
async def submit_delivery_details(order_id: int, request: SubmitDeliveryDetailsRequest, db: AsyncSession = Depends(get_db)) -> SubmitDeliveryDetailsResponse:
    """
    Overview:
    Submit the delivery details for the specified order.

    Function Logic:
    1. Accepts order_id and delivery details (address and order time) as input.
    2. Updates the order in the database with the delivery details.
    3. Returns a confirmation message and delivery time.

    Parameters:
    - order_id (int): The ID of the order to update.
    - request (SubmitDeliveryDetailsRequest): Contains the address ID and order time for the delivery.
    - db (AsyncSession): The database session dependency for querying and updating data.

    Returns:
    - A JSON response conforming to the SubmitDeliveryDetailsResponse model.
    """
    # Mock response for frontend testing
    delivery_time = "now" if request.order_time == "now" else f"Scheduled at {request.order_time}"
    return SubmitDeliveryDetailsResponse(
        order_id=order_id,
        delivery_time=delivery_time,
        message="Delivery details submitted successfully"
    )


@router.get("/orders/{order_id}/payment-summary", response_model=PaymentSummaryResponse)
async def display_payment_summary(order_id: int, db: AsyncSession = Depends(get_db)) -> PaymentSummaryResponse:
    """
    Overview:
    Display the payment summary for the specified order.

    Function Logic:
    1. Accepts order_id as input.
    2. Retrieves the basket value and delivery fee for the order from the database.
    3. Calculates the total amount (basket value + delivery fee).
    4. Returns the payment summary.

    Parameters:
    - order_id (int): The ID of the order for which the payment summary is being displayed.
    - db (AsyncSession): The database session dependency for querying data.

    Returns:
    - A JSON response conforming to the PaymentSummaryResponse model.
    """
    # Mock response for frontend testing
    basket_value = 50.0  # Placeholder value for basket
    delivery_fee = 5.0   # Placeholder value for delivery fee
    total_amount = basket_value + delivery_fee
    items = [
        CartItem(item_id=1, name="Apple", quantity=3, price=1.5),
        CartItem(item_id=2, name="Banana", quantity=2, price=1.0)
    ]
    return PaymentSummaryResponse(
        order_id=order_id,
        basket_value=basket_value,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        items=items
    )
    




@router.post("/orders/{order_id}/cancel", response_model=CancelOrderResponse)
async def cancel_order(order_id: int, db: AsyncSession = Depends(get_db)) -> CancelOrderResponse:
    """
    Overview:
    Cancel the specified order.

    Function Logic:
    1. Accepts order_id as input.
    2. Updates the order status in the database to 'cancelled'.
    3. Returns a confirmation message.

    Parameters:
    - order_id (int): The ID of the order to be cancelled.
    - db (AsyncSession): The database session dependency for querying and updating data.

    Returns:
    - A JSON response conforming to the CancelOrderResponse model.
    """
    # Mock response for frontend testing
    return CancelOrderResponse(
        order_id=order_id,
        message="Order has been cancelled successfully"
    )




@router.get("/orders/{order_id}/track", response_model=TrackOrderResponse)
async def track_order(order_id: int, db: AsyncSession = Depends(get_db)) -> TrackOrderResponse:
    """
    Overview:
    Track the specified order, including ETA and order summary.

    Function Logic:
    1. Accepts order_id as input.
    2. Retrieves the order details including ETA, basket value, delivery fee, and cart items from the database.
    3. Returns the order summary and ETA.

    Parameters:
    - order_id (int): The ID of the order to track.
    - db (AsyncSession): The database session dependency for querying data.

    Returns:
    - A JSON response conforming to the TrackOrderResponse model.
    """
    # Mock response for frontend testing
    eta = "20 minutes"  # Placeholder ETA value
    basket_value = 50.0  # Placeholder value for basket
    delivery_fee = 5.0   # Placeholder value for delivery fee
    total_amount = basket_value + delivery_fee
    items = [
        CartItem(item_id=1, name="Apple", quantity=3, price=1.5),
        CartItem(item_id=2, name="Banana", quantity=2, price=1.0)
    ]
    return TrackOrderResponse(
        order_id=order_id,
        eta=eta,
        basket_value=basket_value,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        items=items,
        message="Order is on the way"
    )



@router.get("/orders/slots", response_model=OrderSlotsResponse)
async def display_order_slots() -> OrderSlotsResponse:
    """
    Overview:
    Display available order slots for scheduling delivery.

    Function Logic:
    1. Returns a list of available delivery slots.

    Returns:
    - A JSON response conforming to the OrderSlotsResponse model.
    """
    # Mock response for frontend testing
    available_slots = ["6am", "9am", "12pm", "3pm", "6pm", "9pm", "now"]
    return OrderSlotsResponse(available_slots=available_slots)



@router.get("/user/addresses", response_model=AddressesResponse)
async def display_addresses(user_id: int, db: AsyncSession = Depends(get_db)) -> AddressesResponse:
    """
    Overview:
    Display the list of saved addresses for the user.

    Function Logic:
    1. Accepts user_id as input.
    2. Retrieves the list of saved addresses for the specified user from the database.
    3. Returns the list of addresses.

    Parameters:
    - user_id (int): The ID of the user whose addresses are being displayed.
    - db (AsyncSession): The database session dependency for querying data.

    Returns:
    - A JSON response conforming to the AddressesResponse model.
    """
    # Mock response for frontend testing
    addresses = [
        Address(address_id=1, address_details="123 Main St, Springfield"),
        Address(address_id=2, address_details="456 Elm St, Shelbyville")
    ]
    return AddressesResponse(addresses=addresses)