'''
Submit Delivery Details (Address (select options), Order Time (Discussed Below),
Top Up Option if wallet balance is below total order + max delivery cost, else it tells you that it’ll deduct total order + max delivery cost from your wallet),
Display Payment Summary (Basket Value, Delivery Fee)
Cancel Order
Track Order (ETA, Summary of Order (Payment Summary + Cart Summary))
display order slots, display adressies
'''




from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import List


class CartItem(BaseModel):
    item_id: int
    name: str
    quantity: int
    price: float



class PaymentSummaryResponse(BaseModel):
   order_id: int
   basket_value: float
   delivery_fee: float
   items: List[CartItem]



class CancelOrderResponse(BaseModel):
    order_id: int
    message: str



class TrackOrderResponse(BaseModel):
    order_id: int
    eta: str
    basket_value: float
    delivery_fee: float
    total_amount: float
    items: List[CartItem]
    message: str


class OrderSlotsResponse(BaseModel):
    available_slots: List[str]


class AddressResponse(BaseModel):
    address_id: int
    address_details: str

class AddressesResponse(BaseModel):
    addresses: List[AddressResponse]


# Schemas for My Orders
class OrderItemDetail(BaseModel):
    item_id: int
    name: str
    price: float
    quantity: int
    total_cost: float

    class Config:
        orm_mode = True

class OrderDetail(BaseModel):
    order_id: int
    total_cost: float
    status: str
    items: List[OrderItemDetail]

    class Config:
        orm_mode = True

# Schemas for Shared Orders
class ContributorDetail(BaseModel):
    user_id: int
    name: str  
    delivery_fee_contribution: float

    class Config:
        orm_mode = True

class SharedOrderDetail(BaseModel):
    order_id: int
    shared_cart_id: int
    total_cost: float
    status: str
    contributors: List[ContributorDetail]
    items: List[OrderItemDetail]
    delivery_fee: float

    class Config:
        orm_mode = True

class OrderDetailResponse(BaseModel):
    """
    Response model for detailed order information.
    """
    order_id: int
    shared_cart_id: Optional[int] = None  # Only populated for shared orders
    total_cost: float
    status: str
    contributors: List[ContributorDetail] = []  # Empty for normal orders
    items: List[OrderItemDetail]
    delivery_fee: float