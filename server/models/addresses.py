from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from .base import Base

class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    building_name = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint('id', 'building_name', name='uq_id_building_name'),
    )

