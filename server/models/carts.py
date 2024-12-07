# list of orders
# cart id
# order slot id
from sqlalchemy import UniqueConstraint
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    supermarket_id = Column(Integer, ForeignKey("supermarkets.id"), nullable=False) 

    user = relationship("User", back_populates="cart")
    supermarket = relationship("Supermarket", back_populates="carts") 
    cart_items = relationship("CartItems", back_populates="cart")
    orders = relationship("Order", back_populates="cart")

    __table_args__ = (
        UniqueConstraint('user_id', name='uq_user_cart'),  # Named unique constraint
    )