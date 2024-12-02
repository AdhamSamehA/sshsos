"""
user_orders
------------
id (Primary Key)
user_id (Foreign Key to users table)
order_id (Foreign Key to orders table)
created_at (Timestamp of when the user placed the order)
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base

# User Orders model
class UserOrder(Base):
    __tablename__ = 'user_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    order_id = Column(Integer, ForeignKey('orders.id'))
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="user_orders")
    order = relationship("Order")