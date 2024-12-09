from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class SharedCartItem(Base):
    __tablename__ = "shared_cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contributor_id = Column(Integer, ForeignKey("shared_cart_contributors.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    contributor = relationship("SharedCartContributor", back_populates="items")
    item = relationship(
        "Item",
        back_populates="shared_cart_items"  # Ensure back_populates is consistent
    )