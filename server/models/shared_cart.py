from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum
from .base import Base
import datetime
from server.enums import SharedCartStatus

class SharedCart(Base):
    __tablename__ = "shared_carts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False)
    order_slot_id = Column(Integer, ForeignKey("order_slots.id"), nullable=False)
    status = Column(Enum(SharedCartStatus), default=SharedCartStatus.OPEN)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    deduction_processed = Column(Boolean, default=False)  # New field

    shared_cart_items = relationship("SharedCartItem", back_populates="shared_cart")
    contributors = relationship("SharedCartContributor", back_populates="shared_cart")
    orders = relationship("Order", back_populates="shared_cart")
    supermarket = relationship("Supermarket", back_populates="shared_carts") 