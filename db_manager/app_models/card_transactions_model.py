from .base import Base
from sqlalchemy import Column, String, TIMESTAMP, Boolean, Integer


class CardTransactions(Base):
    __tablename__ = "card_transactions"

    id = Column(String(255), primary_key=True)
    description = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    amount = Column(Integer(), nullable=False)
    time = Column(TIMESTAMP, nullable=False)
    paid = Column(Boolean, nullable=False, default=False)
    charges = Column(Integer())
    charge_amount = Column(Integer())
    remaining_charges = Column(Integer())
    refund = Column(Boolean, nullable=False, default=False)
