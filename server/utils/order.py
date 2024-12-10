from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from collections import defaultdict
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

from server.models import (
    SharedCart,
    Wallet,
    Supermarket,
    Order,
    OrderSlot,
    SharedCartContributor,
    WalletTransaction,
    OrderItem,
    User
)
from server.enums import SharedCartStatus, OrderStatus, TransactionType


async def find_or_create_shared_cart(
    db: AsyncSession,
    user_id: int,
    supermarket_id: int,
    address_id: int,
    order_slot_id: int
) -> SharedCart:
    """
    Find or create a shared cart with the specified parameters.
    Ensures that the user is added as a contributor to the shared cart.
    """
    try:
        # Fetch the shared cart with eager loading
        shared_cart_result = await db.execute(
            select(SharedCart)
            .options(
                joinedload(SharedCart.shared_cart_items),
                joinedload(SharedCart.contributors),
                joinedload(SharedCart.supermarket)
            )
            .where(
                SharedCart.supermarket_id == supermarket_id,
                SharedCart.address_id == address_id,
                SharedCart.order_slot_id == order_slot_id,
                SharedCart.status == SharedCartStatus.OPEN,
            )
        )
        shared_cart = shared_cart_result.scalars().first()

        if not shared_cart:
            # Create a new shared cart
            shared_cart = SharedCart(
                supermarket_id=supermarket_id,
                address_id=address_id,
                order_slot_id=order_slot_id,
                status=SharedCartStatus.OPEN,
            )
            db.add(shared_cart)
            await db.commit()
            await db.refresh(shared_cart)
            print(f"Created a new shared cart with ID {shared_cart.id}")

        # Check if the user is already a contributor
        contributor_result = await db.execute(
            select(SharedCartContributor)
            .where(
                SharedCartContributor.shared_cart_id == shared_cart.id,
                SharedCartContributor.user_id == user_id,
            )
        )
        contributor = contributor_result.scalars().first()

        if not contributor:
            # Fetch the delivery fee
            delivery_fee_result = await db.execute(
                select(Supermarket.delivery_fee)
                .where(Supermarket.id == supermarket_id)
            )
            delivery_fee = delivery_fee_result.scalar()
            if delivery_fee is None:
                raise HTTPException(status_code=400, detail="Supermarket delivery fee not set.")

            # Add the user as a contributor
            print(f"Adding user ID {user_id} as a contributor to shared cart ID {shared_cart.id}")
            contributor = SharedCartContributor(
                shared_cart_id=shared_cart.id,
                user_id=user_id,
                delivery_fee_contribution=delivery_fee,
            )
            db.add(contributor)
            await db.commit()
            await db.refresh(contributor)

        return shared_cart

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find or create shared cart: {str(e)}")
    
def parse_delivery_time(delivery_time: str) -> datetime:
    """
    Parse the delivery time string (e.g., "6:00AM") into a datetime object for today.
    """
    current_date = datetime.utcnow().date()
    return datetime.strptime(f"{current_date} {delivery_time}", "%Y-%m-%d %I:%M%p")


async def automated_order_placement(db: AsyncSession, user_id : int, shared_cart_id: int, delay: int):
    """
    Finalize the order for the shared cart at the scheduled time.
    """
    await asyncio.sleep(delay)
    print("In automated_order_placement")

    try:
        # Fetch the shared cart and associated order
        try:
            shared_cart_result = await db.execute(
                select(SharedCart)
                .options(
                    joinedload(SharedCart.orders),  
                    joinedload(SharedCart.shared_cart_items),
                    joinedload(SharedCart.supermarket),
                    joinedload(SharedCart.contributors)
                )
                .where(SharedCart.id == shared_cart_id)
            )
            shared_cart = shared_cart_result.scalars().first()

            for item in shared_cart.shared_cart_items:
                print(f"In automatic order placement: Item ID: {item.item_id}, Quantity: {item.quantity}, Price: {item.price}, Contributor ID: {item.contributor_id}")
        
            if not shared_cart:
                raise HTTPException(status_code=400, detail="Shared cart not found.")

            # Ensure there is an order associated with this shared cart
            if not shared_cart.orders:
                raise HTTPException(status_code=400, detail="No order associated with this shared cart.")
            
            order = shared_cart.orders[0] 
        except Exception as e:
            print(f"Error in automated_order_placement--fetching shared cart and associated order: {e}")
            return
        
        try:
            # Fetch delivery fee from the supermarket
            delivery_fee = shared_cart.supermarket.delivery_fee
            if delivery_fee is None:
                print(f"Supermarket delivery fee not set for shared cart ID {shared_cart_id}.")
                return 
        except Exception as e:
            print(f"Error in automated_order_placement--fetching delivery fee from the supermarket: {e}")
            return
         
        try:
            contributors = shared_cart.contributors
            if not contributors:
                print(f"No contributors found in shared cart ID {shared_cart_id}.")
                return  # Early exit since no contributors exist
        except Exception as e:
            print(f"Error in automated_order_placement--fetching contributors: {e}")
            return 

        # Update delivery fee contributions if necessary
        await update_delivery_fee_contribution(db, shared_cart)

        # Aggregate shared cart items
        #aggregated_items = await aggregate_shared_cart_items(shared_cart.shared_cart_items)

        # Calculate total item cost
        #total_item_cost = sum(data["total_price"] for data in aggregated_items.values())

        # Calculate total cost (items + delivery fee)
        #total_cost = total_item_cost + delivery_fee

        # Update the order details
        order.status = OrderStatus.PLACED
        #order.total_amount = total_cost
        db.add(order)

        # Add aggregated items to the order
        #for item_id, data in aggregated_items.items():
        #        order_item = OrderItem(
        #            order_id=order.id,
       #             item_id=item_id,
       #             quantity=data["quantity"],
       #             price=data["total_price"] / data["quantity"], 
       #         )
       #         db.add(order_item)

        # Update shared cart status to CLOSED
        shared_cart.status = SharedCartStatus.CLOSED
        db.add(shared_cart)

        # Commit the changes to update the order and cart
        await db.commit()

        # Calculate the split of the delivery fee among contributors
        num_contributors = len(contributors)
        split_delivery_fee = delivery_fee / num_contributors
        print(f"SPLIT DELIVERY FEE: {split_delivery_fee}")

        
        # Process refunds: Contributors are refunded the difference between their initial contribution and the split fee
        #for contributor in contributors:
        initial_contribution = delivery_fee
        print(f"INITIAL CONTRIBUTION: {initial_contribution}")
        refund_amount = initial_contribution - split_delivery_fee
        print(f"REFUND AMOUNT: {refund_amount}")

        if refund_amount > 0:
            try:
                    # Use the process_payment function to issue a refund
                    await process_payment_by_amount(
                        db=db,
                        user_id=user_id,
                        amount=refund_amount,
                        transaction_type=TransactionType.REFUND,
                    )
                    print(f"Refund of {refund_amount} processed for User ID {user_id}")
            except Exception as e:
                print(f"Failed to process refund for User ID {user_id}: {e}")

                
        # Commit the refunds to the database
        await db.commit()
        

    except Exception as e:
        print(f"Internal Server Error in automated_order_placement for shared cart ID {shared_cart_id}: {e}")

async def update_delivery_fee_contribution(db: AsyncSession, shared_cart: SharedCart):
    """
    Updates the delivery fee contributions for each contributor based on the finalized order.
    """
    # Example logic:
    total_delivery_fee = shared_cart.supermarket.delivery_fee
    num_contributors = len(shared_cart.contributors)
    split_delivery_fee = total_delivery_fee / num_contributors

    for contributor in shared_cart.contributors:
        contributor.delivery_fee_contribution = split_delivery_fee
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

def aggregate_items(items: List[Any]) -> List[Dict[str, Any]]:
    """
    Aggregates items by item_id, summing quantities and calculating total_cost.

    Parameters:
    - items: List of OrderItem or SharedCartItem instances.

    Returns:
    - List of dictionaries with aggregated item details.
    """
    aggregated = defaultdict(lambda: {"quantity": 0, "total_cost": 0.0, "price": 0.0, "item": None})

    for item in items:
        item_id = item.item.id  # Assuming `item` relationship is loaded
        aggregated[item_id]["quantity"] += item.quantity
        aggregated[item_id]["total_cost"] += item.price * item.quantity
        aggregated[item_id]["price"] = item.price  # Assuming price per unit is consistent
        aggregated[item_id]["item"] = item.item  # Store the Item instance for details

    # Convert to list of dictionaries
    aggregated_list = []
    for item_id, data in aggregated.items():
        aggregated_list.append({
            "item_id": item_id,
            "name": data["item"].name,
            "price": data["price"],
            "quantity": data["quantity"],
            "total_cost": data["total_cost"],
        })

    return aggregated_list


async def deduct_delivery_fee_contributions(db: AsyncSession, shared_cart: SharedCart):
    print("In deduct_delivery_fee_contributions")
    """
    Deducts the delivery fee contributions from each contributor's wallet.
    """
    # Check if deduction has already been processed
    if shared_cart.deduction_processed:
        print(f"Deduction already processed for cart ID {shared_cart.id}. Skipping.")
        return
    contributors = shared_cart.contributors
    print(f"Number of contributors: {len(contributors)}")
    if not contributors:
        print(f"No contributors found in shared cart ID {shared_cart.id}.")
        raise HTTPException(status_code=400, detail="No contributors found in shared cart.")

    for contributor in contributors:
        user_id = contributor.user.id
        initial_contribution = contributor.delivery_fee_contribution
        print(f"Initial Contribution for user {user_id} is {initial_contribution}")

        # Calculate current balance
        balance = await get_wallet_balance(db, user_id)
        print(f"User ID {user_id} - Current Balance: {balance}")

        if balance < initial_contribution:
            print(f"Insufficient balance for User ID {user_id}. Required: {initial_contribution}, Available: {balance}")
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance for User ID {user_id}. Required: {initial_contribution}, Available: {balance}"
            )

        # Create a WalletTransaction for the deduction
        wallet_transaction = WalletTransaction(
            wallet_id=contributor.user.wallet.id,
            user_id=user_id,
            amount=-initial_contribution,  
            transaction_type=TransactionType.DEBIT,
            created_at=datetime.utcnow(),
        )
        db.add(wallet_transaction)
        print(f"Deducted {initial_contribution} from User ID {user_id}'s wallet.")
        balance = await get_wallet_balance(db, user_id)
        print(f"User ID {user_id} - Current Balance: {balance}")


    # Commit all deductions at once
    await db.commit()
    print(f"Deducted delivery fee contributions from {len(contributors)} contributors.")


async def get_wallet_balance(db: AsyncSession, user_id: int) -> float:
    result = await db.execute(
        select(func.sum(WalletTransaction.amount))
        .where(WalletTransaction.user_id == user_id)
    )
    total = result.scalar() or 0.0
    return total


async def add_contributor_to_shared_cart(
    db: AsyncSession, user_id: int, supermarket_id: int, address_id: int, order_slot_id: int
):
    """
    Adds a contributor to the shared cart if they are not already a contributor.
    Initially sets the delivery fee contribution to the maximum delivery fee.
    """
    try:
        # Step 1: Find or create shared cart
        try:
            shared_cart = await find_or_create_shared_cart(
                db=db,
                user_id=user_id,
                supermarket_id=supermarket_id,
                address_id=address_id,
                order_slot_id=order_slot_id,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error finding or creating shared cart: {str(e)}")

        # Step 2: Check if the user is already a contributor
        try:
            contributor_result = await db.execute(
                select(SharedCartContributor)
                .where(
                    SharedCartContributor.shared_cart_id == shared_cart.id,
                    SharedCartContributor.user_id == user_id,
                )
            )
            existing_contributor = contributor_result.scalars().first()
            if existing_contributor:
                print(f"User ID {user_id} is already a contributor to Shared Cart ID {shared_cart.id}.")
                return existing_contributor
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error checking existing contributors: {str(e)}")

        # Step 3: Fetch the user
        try:
            user = await db.get(User, user_id)
            if not user:
                print(f"User ID {user_id} does not exist.")
                raise HTTPException(status_code=400, detail="User does not exist.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

        # Step 4: Fetch the supermarket delivery fee
        try:
            supermarket = shared_cart.supermarket
            if not supermarket or supermarket.delivery_fee is None:
                print(f"Supermarket associated with Shared Cart ID {shared_cart.id} does not have a delivery fee set.")
                raise HTTPException(status_code=400, detail="Supermarket delivery fee not set.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching supermarket delivery fee: {str(e)}")

        # Step 5: Set the user's initial delivery fee contribution
        try:
            delivery_fee_contribution = supermarket.delivery_fee
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error setting delivery fee contribution: {str(e)}")

        # Step 6: Create and add the new contributor
        try:
            new_contributor = SharedCartContributor(
                shared_cart_id=shared_cart.id,
                user_id=user_id,
                delivery_fee_contribution=delivery_fee_contribution,
            )
            db.add(new_contributor)
            await db.commit()
            print(
                f"Added User ID {user_id} as a contributor to Shared Cart ID {shared_cart.id} "
                f"with a delivery fee contribution of {delivery_fee_contribution}."
            )
            return new_contributor
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding contributor: {str(e)}")

    except HTTPException as http_exc:
        print(f"HTTP Exception in add_contributor_to_shared_cart: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        print(f"Unexpected Exception in add_contributor_to_shared_cart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def process_payment(
    db: AsyncSession,
    user_id: int,
    delivery_fee: float,
    shared_cart_items
):
    print(f"In Process Payment For User: {user_id}")
    """
    Process a single payment for the user for the shared cart.

    Args:
        db: Database session.
        user_id: ID of the user making the payment.
        shared_cart: The shared cart object.
        delivery_fee: The delivery fee to be shared across contributors.
    """
    # Fetch the user and their wallet
    user = await db.execute(
        select(User)
        .options(joinedload(User.wallet))
        .where(User.id == user_id)
    )
    user = user.scalars().first()

    if not user or not user.wallet:
        raise HTTPException(status_code=404, detail=f"User or wallet not found for user ID {user_id}.")

    wallet_id = user.wallet.id

    # Get the user's wallet balance
    wallet_balance = await get_wallet_balance(db, user_id)

    # Calculate total cost for the user

    for item in shared_cart_items:
        print(f"In Process Payment: Item ID: {item.item_id}, Quantity: {item.quantity}, Price: {item.price}, Contributor ID: {item.contributor_id}")
    
    user_items = [
        item for item in shared_cart_items if item.contributor_id == user_id
    ]
    print(f"User Items for User {user_id}:")

    if user_items:
        for item in user_items:
            print(
                f"Item ID: {item.id}, Price: {item.price}, "
                f"Quantity: {item.quantity}, Total Cost: {item.price * item.quantity}"
            )
    else:
        print("No items found for this user.")

    total_item_cost = sum(item.price * item.quantity for item in user_items)
    total_cost = total_item_cost + delivery_fee

    # Check wallet balance
    if wallet_balance < total_cost:
        raise HTTPException(status_code=400, detail=f"Insufficient balance for user ID {user_id}.")

    # Deduct from wallet by adding a new transaction
    transaction = WalletTransaction(
        wallet_id=wallet_id,
        user_id=user_id,
        amount=-total_cost,
        transaction_type=TransactionType.DEBIT,
        created_at=datetime.utcnow(),
    )
    db.add(transaction)
    await db.commit()

    print(f"Processed payment of {total_cost} for user ID {user_id}.")


async def process_payment_by_amount(
    db: AsyncSession,
    user_id: int,
    amount: float,
    transaction_type: TransactionType = TransactionType.DEBIT,
):
    """
    Process a payment or refund for the user based on a specified amount.

    Args:
        db: Database session.
        user_id: ID of the user making the payment.
        amount: The amount to be processed (negative for refunds).
        transaction_type: Type of transaction (DEBIT for payments, REFUND for refunds).
    """
    print(f"Processing {transaction_type} of amount {amount} for User ID {user_id}")

    # Fetch the user and their wallet
    user = await db.execute(
        select(User)
        .options(joinedload(User.wallet))
        .where(User.id == user_id)
    )
    user = user.scalars().first()

    if not user or not user.wallet:
        raise HTTPException(status_code=404, detail=f"User or wallet not found for user ID {user_id}.")

    wallet_id = user.wallet.id

    # Get the user's wallet balance
    wallet_balance = await get_wallet_balance(db, user_id)

    # For DEBIT transactions, ensure sufficient balance
    if transaction_type == TransactionType.DEBIT and wallet_balance < amount:
        raise HTTPException(status_code=400, detail=f"Insufficient balance for user ID {user_id}.")

    # Add the transaction
    transaction = WalletTransaction(
        wallet_id=wallet_id,
        user_id=user_id,
        amount=-amount if transaction_type == TransactionType.DEBIT else amount,
        transaction_type=transaction_type,
        created_at=datetime.utcnow(),
    )
    db.add(transaction)
    await db.commit()

    print(f"{transaction_type} of {amount} processed for User ID {user_id}.")
