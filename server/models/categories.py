### category id
### category name: (Dairy & Eggs, Fruits & Vegetables, Bakery, Nuts & Seeds, Chips & Snacks, Cereals & Packets, Hygiene & Personal Care, Stationary)

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base

# Categories model
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    items = relationship("Item", back_populates="category")

    supermarket_categories = relationship("SupermarketCategory", back_populates="category")