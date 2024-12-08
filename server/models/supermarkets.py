## id
## supermarket name
## supermarket address
### supermarket phone number
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base

# Supermarkets model
class Supermarket(Base):
    __tablename__ = 'supermarkets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    photo_url = Column(String)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    delivery_fee = Column(Float, nullable=False)

    items = relationship("Item", back_populates="supermarket")
    carts = relationship("Cart", back_populates="supermarket")
    order_slots = relationship("OrderSlot", back_populates="supermarket")
    supermarket_categories = relationship("SupermarketCategory", back_populates="supermarket")
    stock_levels = relationship("StockLevel", back_populates="supermarket")
    shared_carts = relationship("SharedCart", back_populates="supermarket")