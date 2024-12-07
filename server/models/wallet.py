## id
## balance

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from .base import Base

# Wallet model
class Wallet(Base):
    __tablename__ = 'wallet'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    balance = Column(Float, default=0.0)

    user = relationship("User")

    __table_args__ = (
        UniqueConstraint('user_id', name='uq_user_wallet'),
    )