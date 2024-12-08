# order_items id
# order id
# user who made the order
# address id
# delivery fee
# order status
# supermarket id

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from .base import Base
import enum

# Enumerations for order status
class OrderStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"

# Order model
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    address_id = Column(Integer, ForeignKey('addresses.id'))
    delivery_fee = Column(Float, nullable=False)
    total_amount= Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    supermarket_id = Column(Integer, ForeignKey('supermarkets.id'))
    cart_id = Column(Integer, ForeignKey('carts.id'))
    shared_cart_id = Column(Integer, ForeignKey("shared_carts.id"), nullable=True)  # Nullable for individual orders
    order_slot_id = Column(Integer, ForeignKey("order_slots.id"), nullable=False)

    user = relationship("User", back_populates="orders")
    address = relationship("Address")
    order_items = relationship("OrderItem", back_populates="order")
    supermarket = relationship("Supermarket")
    cart = relationship("Cart", back_populates="orders")
    shared_cart = relationship("SharedCart", back_populates="orders")  # New relationship with shared carts
    order_slot = relationship("OrderSlot", back_populates="orders")
    #items = relationship("SharedCartItem", back_populates="order") 

    __table_args__ = (
        UniqueConstraint('cart_id', name='uq_cart_order'),
        UniqueConstraint('shared_cart_id', name='uq_shared_cart_order')
    )