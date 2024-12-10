from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import joinedload
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from server.dependencies import get_db
from server.schemas import SubmitDeliveryDetailsRequest, SubmitDeliveryDetailsResponse, PaymentSummaryResponse, CancelOrderResponse, TrackOrderResponse, OrderSlotsResponse, AddressesResponse, CartItem, OrderItemDetail, OrderDetail, ContributorDetail, SharedOrderDetail, AddressResponse, OrderDetailResponse, ContributorContribution
from server.models import SharedCartItem, Order, SharedCart, SharedCartContributor, OrderItem, OrderSlot, Address
from server.utils import aggregate_items
from typing import List
router = APIRouter()

@router.get("/orders/{order_id}/payment-summary", response_model=PaymentSummaryResponse)
async def display_payment_summary(order_id: int, db: AsyncSession = Depends(get_db)) -> PaymentSummaryResponse:
    """
    Display the payment summary for the specified order.
    """
    try:
        # Fetch the order with related items and details
        result = await db.execute(
            select(Order)
            .options(
                joinedload(Order.order_items).joinedload(OrderItem.item)
            )
            .where(Order.id == order_id)
        )
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")

        # Calculate basket value
        basket_value = sum(
            item.price * item.quantity for item in order.order_items
        )

        # Retrieve delivery fee
        delivery_fee = order.delivery_fee or 0.0

        # Calculate total amount
        total_amount = basket_value + delivery_fee

        # Build item details
        items = [
            CartItem(
                item_id=item.item.id,
                name=item.item.name,
                quantity=item.quantity,
                price=item.price,
            )
            for item in order.order_items
        ]

        return PaymentSummaryResponse(
            order_id=order.id,
            basket_value=basket_value,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            items=items,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payment summary: {e}")
    

@router.get("/order/details", response_model=OrderDetailResponse)
async def get_order_details(
    order_id: int = Query(..., description="The ID of the order to fetch details for"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch detailed information for a specific order (normal or shared).

    Parameters:
    - order_id: ID of the order to fetch details.

    Returns:
    - Detailed information about the order, including items, contributors (for shared orders), and costs.
    """
    try:
        # Query the Order table with joined relationships
        result = await db.execute(
            select(Order)
            .options(
                joinedload(Order.order_items).joinedload(OrderItem.item),
                joinedload(Order.shared_cart).joinedload(SharedCart.shared_cart_items).joinedload(SharedCartItem.item),
                joinedload(Order.shared_cart).joinedload(SharedCart.contributors).joinedload(SharedCartContributor.user),
            )
            .where(Order.id == order_id)
        )
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")

        # Check if this is a shared order
        if order.shared_cart:
            # Shared order details
            contributors = [
                ContributorDetail(
                    user_id=contributor.user.id,
                    name=contributor.user.name,
                    delivery_fee_contribution=contributor.delivery_fee_contribution,
                )
                for contributor in order.shared_cart.contributors
            ]

            # Aggregate shared cart items
            aggregated_items = aggregate_items(order.shared_cart.shared_cart_items)

            return OrderDetailResponse(
                order_id=order.id,
                shared_cart_id=order.shared_cart.id,
                total_cost=order.total_amount,
                status=order.status.value,
                contributors=contributors,
                items=aggregated_items,
                delivery_fee=order.delivery_fee,
            )
        else:
            # Normal order details
            # Aggregate order items
            aggregated_items = aggregate_items(order.order_items)

            return OrderDetailResponse(
                order_id=order.id,
                total_cost=order.total_amount,
                status=order.status.value,
                contributors=[],  # No contributors for normal orders
                items=aggregated_items,
                delivery_fee=order.delivery_fee,
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch order details: {e}")


@router.get("/orders/slots", response_model=OrderSlotsResponse)
async def display_order_slots(
    supermarket_id: int = Query(..., description="The ID of the supermarket"),
    db: AsyncSession = Depends(get_db)
) -> OrderSlotsResponse:
    """
    Display available order slots for a specific supermarket.

    Function Logic:
    1. Accepts supermarket_id as input.
    2. Retrieves the list of available delivery slots for the specified supermarket.
    3. Returns the list of delivery slots.

    Parameters:
    - supermarket_id (int): The ID of the supermarket for which slots are being fetched.
    - db (AsyncSession): The database session dependency for querying data.

    Returns:
    - A JSON response conforming to the OrderSlotsResponse model.
    """
    try:
        # Fetch order slots for the specified supermarket
        result = await db.execute(
            select(OrderSlot).where(OrderSlot.supermarket_id == supermarket_id)
        )
        slots = result.scalars().all()

        if not slots:
            raise HTTPException(status_code=404, detail="No order slots found for the specified supermarket.")

        # Extract delivery times
        available_slots = [slot.delivery_time for slot in slots]
        return OrderSlotsResponse(available_slots=available_slots)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch order slots: {e}")


@router.get("/user/addresses", response_model=AddressesResponse)
async def display_addresses(user_id: int, db: AsyncSession = Depends(get_db)) -> AddressesResponse:
    """
    Overview:
    Display the list of all saved addresses.

    Function Logic:
    1. Retrieves all saved addresses from the database.
    2. Returns the list of addresses.

    Parameters:
    - db (AsyncSession): The database session dependency for querying data.

    Returns:
    - A JSON response conforming to the AddressesResponse model.
    """
    try:
        result = await db.execute(select(Address))
        addresses = result.scalars().all()

        if not addresses:
            return AddressesResponse(addresses=[])

        address_responses = [
            AddressResponse(address_id=address.id, address_details=address.building_name)
            for address in addresses
        ]
        return AddressesResponse(addresses=address_responses)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch addresses: {e}")


@router.get("/orders", response_model=List[OrderDetail])
async def view_my_orders(
    user_id: int = Query(..., description="The ID of the user"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all normal orders placed by the specified user with a detailed item breakdown.
    Excludes shared orders.
    """
    try:
        # Query normal orders for the user (exclude shared_cart_id)
        result = await db.execute(
            select(Order)
            .options(
                joinedload(Order.order_items).joinedload(OrderItem.item),  # Load order items and related items
                joinedload(Order.address),
                joinedload(Order.supermarket),
            )
            .where(Order.user_id == user_id, Order.shared_cart_id.is_(None))  # Exclude shared orders
        )
        orders = result.unique().scalars().all()  # Use .unique() to handle joined eager loads

        if not orders:
            return []

        # Structure the response
        order_details = []
        for order in orders:
            items = [
                OrderItemDetail(
                    item_id=item.item.id,
                    name=item.item.name,
                    price=item.item.price,
                    quantity=item.quantity,
                    total_cost=item.price * item.quantity,
                )
                for item in order.order_items
            ]
            order_detail = OrderDetail(
                order_id=order.id,
                total_cost=order.total_amount,
                status=order.status.value,
                address=order.address.building_name,
                supermarket=order.supermarket.name,
                items=items,
            )
            order_details.append(order_detail)

        return order_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {e}")


@router.get("/shared-orders", response_model=List[SharedOrderDetail])
async def view_shared_orders(
    user_id: int = Query(..., description="The ID of the user"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all shared orders where the user is a contributor with detailed breakdown.
    """
    try:
        # Fetch shared cart IDs where the user is a contributor
        contributor_result = await db.execute(
            select(SharedCartContributor.shared_cart_id)
            .where(SharedCartContributor.user_id == user_id)
        )
        shared_cart_ids = [row[0] for row in contributor_result.fetchall()]

        if not shared_cart_ids:
            return []

        # Fetch shared carts
        shared_carts_result = await db.execute(
            select(SharedCart)
            .options(
                joinedload(SharedCart.orders).joinedload(Order.order_items).joinedload(OrderItem.item),
                joinedload(SharedCart.contributors).joinedload(SharedCartContributor.user),
                joinedload(SharedCart.shared_cart_items).joinedload(SharedCartItem.item),
                joinedload(SharedCart.supermarket),
            )
            .where(SharedCart.id.in_(shared_cart_ids))
            .order_by(SharedCart.created_at.desc())
        )
        shared_carts = shared_carts_result.unique().scalars().all()

        shared_order_details = []

        for shared_cart in shared_carts:
            # Fetch contributors
            contributors = [
                ContributorDetail(
                    user_id=contributor.user.id,
                    name=contributor.user.name,
                    delivery_fee_contribution=contributor.delivery_fee_contribution,
                )
                for contributor in shared_cart.contributors
            ]

            # Fetch items
            for order in shared_cart.orders:
                items = [
                    OrderItemDetail(
                        item_id=item.item.id,
                        name=item.item.name,
                        price=item.item.price,
                        quantity=item.quantity,
                        total_cost=item.price * item.quantity,
                    )
                    for item in order.order_items
                ]

                shared_order_detail = SharedOrderDetail(
                    order_id=order.id,
                    shared_cart_id=shared_cart.id,
                    total_cost=order.total_amount,
                    status=order.status.value,
                    contributors=contributors,
                    items=items,
                    delivery_fee=shared_cart.supermarket.delivery_fee,
                )
                shared_order_details.append(shared_order_detail)

        return shared_order_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch shared orders: {e}")


@router.get("/shared-orders-test", response_model=List[SharedOrderDetail])
async def view_shared_orders(
    user_id: int = Query(..., description="The ID of the user"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch all shared orders where the user is a contributor with detailed breakdown.
    Includes information on who ordered what, their contribution to the total order, and the items they contributed.
    """
    try:
        # Step 1: Fetch shared cart IDs where the user is a contributor
        contributor_result = await db.execute(
            select(SharedCartContributor.shared_cart_id)
            .where(SharedCartContributor.user_id == user_id)
        )
        shared_cart_ids = [row[0] for row in contributor_result.fetchall()]

        if not shared_cart_ids:
            return []

        # Step 2: Fetch shared carts with related data
        shared_carts_result = await db.execute(
            select(SharedCart)
            .options(
                joinedload(SharedCart.orders).joinedload(Order.order_items).joinedload(OrderItem.item),
                joinedload(SharedCart.contributors).joinedload(SharedCartContributor.user),
                joinedload(SharedCart.shared_cart_items).joinedload(SharedCartItem.item),
                joinedload(SharedCart.supermarket),
            )
            .where(SharedCart.id.in_(shared_cart_ids))
            .order_by(SharedCart.created_at.desc())
        )
        shared_carts = shared_carts_result.unique().scalars().all()

        shared_order_details = []

        # Step 3: Process shared carts
        for shared_cart in shared_carts:
            # Step 3.1: Fetch delivery fee from supermarket
            delivery_fee = shared_cart.supermarket.delivery_fee or 0.0
            num_contributors = len(shared_cart.contributors)
            split_delivery_fee = delivery_fee / num_contributors if num_contributors > 0 else 0.0

            # Step 3.2: Aggregate contributor details
            contributor_contributions = []
            for contributor in shared_cart.contributors:
                # Fetch items contributed by the user
                user_items = [
                    OrderItemDetail(
                        item_id=item.item.id,
                        name=item.item.name,
                        price=item.price,
                        quantity=item.quantity,
                        total_cost=item.price * item.quantity,
                    )
                    for item in shared_cart.shared_cart_items
                    if item.contributor_id == contributor.id
                ]

                # Calculate the user's total contribution (items + delivery fee)
                delivery_fee_contribution = contributor.delivery_fee_contribution or 0.0
                total_contribution = sum(item.total_cost for item in user_items) + delivery_fee_contribution

                # Add contributor details
                contributor_contributions.append(
                    ContributorContribution(
                        user_id=contributor.user.id,
                        name=contributor.user.name,
                        delivery_fee_contribution=delivery_fee_contribution,
                        total_contribution=total_contribution,
                        items=user_items,
                    )
                )

            # Step 3.3: Process orders in the shared cart
            for order in shared_cart.orders:
                # Prepare item list for the order
                items = [
                    OrderItemDetail(
                        item_id=item.item.id,
                        name=item.item.name,
                        price=item.item.price,
                        quantity=item.quantity,
                        total_cost=item.price * item.quantity,
                    )
                    for item in order.order_items
                ]

                shared_order_detail = SharedOrderDetail(
                    order_id=order.id,
                    shared_cart_id=shared_cart.id,
                    total_cost=order.total_amount,
                    status=order.status.value,
                    contributions=contributor_contributions,
                    items=items,
                    delivery_fee=delivery_fee,
                )
                shared_order_details.append(shared_order_detail)

        return shared_order_details

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch shared orders: {e}")
