from .base import Base
from sqlalchemy import Column, String, TIMESTAMP, Integer


class CardBills(Base):
    __tablename__ = "card_bills"

    close_date = Column(TIMESTAMP, primary_key=True)
    state = Column(String(255), nullable=False)
    amount = Column(Integer(), nullable=False)
