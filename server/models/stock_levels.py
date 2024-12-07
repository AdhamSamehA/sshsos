"""
stock_levels
------------
id
item_id
supermarket_id
quantity
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base

# Stock Levels model
class StockLevel(Base):
    __tablename__ = 'stock_levels'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    supermarket_id = Column(Integer, ForeignKey('supermarkets.id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    item = relationship("Item")
    supermarket = relationship("Supermarket")