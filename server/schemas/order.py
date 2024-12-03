'''
Submit Delivery Details (Address (select options), Order Time (Discussed Below),
Top Up Option if wallet balance is below total order + max delivery cost, else it tells you that it’ll deduct total order + max delivery cost from your wallet),
Display Payment Summary (Basket Value, Delivery Fee)
Cancel Order
Track Order (ETA, Summary of Order (Payment Summary + Cart Summary))
display order slots, display adressies
'''




from pydantic import BaseModel
from typing import Optional
from typing import List



class SubmitDeliveryDetailsRequest(BaseModel):
   address_id: int
   order_time: str  # Can be one of '6am', '9am', '12pm', '3pm', '6pm', '9pm', or 'now'




class SubmitDeliveryDetailsResponse(BaseModel):
   order_id: int
   delivery_time: str
   message: str




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


class Address(BaseModel):
    address_id: int
    address_details: str

class AddressesResponse(BaseModel):
    addresses: List[Address]

