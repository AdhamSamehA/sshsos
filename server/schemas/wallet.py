from pydantic import BaseModel, Field

# Request model for topping up the wallet
class WalletTopUpRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to add to the wallet.")

# Response model for wallet operations
class WalletResponse(BaseModel):
    wallet_id: int
    balance: float
    message: str

# Request model for paying from the wallet
class WalletPaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount to deduct from the wallet.")