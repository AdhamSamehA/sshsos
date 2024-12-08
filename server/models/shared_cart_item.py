from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class SharedCartItem(Base):
    __tablename__ = "shared_cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    #order_id = Column(Integer, ForeignKey('orders.id'), nullable=False) 
    shared_cart_id = Column(Integer, ForeignKey('shared_carts.id'), nullable=False)
    contributor_id = Column(Integer, ForeignKey("shared_cart_contributors.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    shared_cart = relationship("SharedCart", back_populates="shared_cart_items")
    contributor = relationship("SharedCartContributor", back_populates="items")
    item = relationship(
        "Item",
        back_populates="shared_cart_items"  # Ensure back_populates is consistent
    )
    #order = relationship("Order", back_populates="items")