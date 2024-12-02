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

    orders = relationship("Order", back_populates="user")
    user_orders = relationship("UserOrder", back_populates="user")