from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base



class SharedCartContributor(Base):
    __tablename__ = "shared_cart_contributors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shared_cart_id = Column(Integer, ForeignKey("shared_carts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    delivery_fee_contribution = Column(Float, nullable=True)

    shared_cart = relationship("SharedCart", back_populates="contributors")
    items = relationship("SharedCartItem", back_populates="contributor")
    user = relationship("User", back_populates="shared_cart_contributors")