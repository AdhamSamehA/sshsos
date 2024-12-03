from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class SupermarketCategory(Base):
    __tablename__ = 'supermarket_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supermarket_id = Column(Integer, ForeignKey('supermarkets.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    # Relationships for ORM convenience
    supermarket = relationship("Supermarket", back_populates="supermarket_categories")
    category = relationship("Category", back_populates="supermarket_categories")
