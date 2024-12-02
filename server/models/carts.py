# list of orders
# cart id
# order slot id

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base

# Carts model
class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_slot_id = Column(Integer, ForeignKey('order_slots.id'))

    order_slot = relationship("OrderSlot")