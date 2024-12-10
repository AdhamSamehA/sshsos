from pydantic import BaseModel, Field
from datetime import datetime

# Request model for topping up the wallet
class WalletTopUpRequest(BaseModel):
    user_id : int
    amount: float = Field(..., gt=0, description="Amount to add to the wallet.")

# Response model for wallet operations
class WalletResponse(BaseModel):
    wallet_id: int
    balance: float
    message: str

# Request model for paying from the wallet
class WalletPaymentRequest(BaseModel):
    user_id : int
    amount: float = Field(..., gt=0, description="Amount to deduct from the wallet.")

class WalletTransactionResponse(BaseModel):
    id: int
    wallet_id: int
    user_id: int
    amount: float
    transaction_type: str
    created_at: datetime

    class Config:
        orm_mode = True