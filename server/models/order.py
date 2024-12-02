# order_items id
# order id
# user who made the order
# address id
# delivery fee
# order status
# supermarket id

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from .base import Base
import enum

# Enumerations for order status
class OrderStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Order model
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    address_id = Column(Integer, ForeignKey('addresses.id'))
    delivery_fee = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    supermarket_id = Column(Integer, ForeignKey('supermarkets.id'))

    user = relationship("User", back_populates="orders")
    address = relationship("Address")
    order_items = relationship("OrderItem", back_populates="order")
    supermarket = relationship("Supermarket")