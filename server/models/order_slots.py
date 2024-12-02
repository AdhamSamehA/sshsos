## id
## Order slot (6:00AM, 9:00AM, 12:00PM, 3:00PM, 6:00PM, 9:00PM, 12:00AM)
## supermarket id (Order slots differ for each supermarket)

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from .base import Base

# Order Slots model
class OrderSlot(Base):
    __tablename__ = 'order_slots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_slot = Column(String, nullable=False)
    supermarket_id = Column(Integer, ForeignKey('supermarkets.id'))

    supermarket = relationship("Supermarket", back_populates="order_slots")