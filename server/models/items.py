## item id
## item name
## item photo url
## item price
## item description
## item category (id)
## supermarket id

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base

# Items model
class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    photo_url = Column(String)
    price = Column(Float, nullable=False)
    description = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'))
    supermarket_id = Column(Integer, ForeignKey('supermarkets.id'))

    category = relationship("Category", back_populates="items")
    supermarket = relationship("Supermarket", back_populates="items")
    stock_levels = relationship("StockLevel", back_populates="item")