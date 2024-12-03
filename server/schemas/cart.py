#put all requests and responses related to cart API here

from pydantic import BaseModel
from typing import List

class CreateCartRequest(BaseModel):
    supermarket_id: int
    user_id: int


class CartResponse(BaseModel):
    cart_id: int
    supermarket_id: int
    message: str


class AddItemRequest(BaseModel):
    item_id: int
    quantity: int

class RemoveItemRequest(BaseModel):
    item_id: int

#view cart
class CartItem(BaseModel):
    item_id: int
    name: str
    quantity: int
    price: float
    photo_url: str

class ViewCartResponse(BaseModel):
    cart_id: int
    items: List[CartItem]
    total_price: float
    wallet_balance: float


class UpdateCartItem(BaseModel):
    item_id: int
    quantity: int

class UpdateCartRequest(BaseModel):
    items: List[UpdateCartItem]