from pydantic import BaseModel
from typing import List
from datetime import datetime

# Response model for account details
class AccountDetailsResponse(BaseModel):
    wallet_balance: float
    default_address: str
    total_orders: int

# Response model for an individual order
class OrderSummary(BaseModel):
    order_id: int
    date: datetime
    total_amount: float
    status: str

# Response model for user order history
class OrderHistoryResponse(BaseModel):
    user_id: int
    orders: List[OrderSummary]
