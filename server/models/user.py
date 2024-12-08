# user id
# wallet id
# user_order id
# name

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base

# User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    default_address_id = Column(Integer, ForeignKey('addresses.id'), nullable=True)

    orders = relationship("Order", back_populates="user")
    user_orders = relationship("UserOrder", back_populates="user")
    default_address = relationship("Address")
    cart = relationship("Cart", back_populates="user")
    transactions = relationship("WalletTransaction", back_populates="user", cascade="all, delete-orphan")
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    shared_cart_contributors = relationship("SharedCartContributor", back_populates="user")