import enum

# Enumerations for order status
class OrderStatus(enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    PLACED = "placed"
    COMPLETED = "completed"
    CANCELED = "canceled"