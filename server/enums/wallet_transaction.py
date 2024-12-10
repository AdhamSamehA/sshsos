import enum
# Define Enum for Transaction Types
class TransactionType(enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    REFUND = "refund"