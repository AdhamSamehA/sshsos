from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from .base import Base
import datetime
import enum


# Enumerations for shared cart status
class SharedCartStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"

class SharedCart(Base):
    __tablename__ = "shared_carts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False)
    order_slot_id = Column(Integer, ForeignKey("order_slots.id"), nullable=False)
    status = Column(Enum(SharedCartStatus), default=SharedCartStatus.OPEN)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    shared_cart_items = relationship("SharedCartItem", back_populates="shared_cart")
    contributors = relationship("SharedCartContributor", back_populates="shared_cart")
    orders = relationship("Order", back_populates="shared_cart")
    supermarket = relationship("Supermarket", back_populates="shared_carts") 