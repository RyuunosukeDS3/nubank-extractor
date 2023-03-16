from .base import Base
from sqlalchemy import Column, String, TIMESTAMP, Integer


class AccountTransactions(Base):
    __tablename__ = "account_transactions"

    id = Column(String(255), primary_key=True)
    payment_type = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)
    endpoint = Column(String(255), nullable=False)
    time = Column(TIMESTAMP, nullable=False)
    amount = Column(Integer(), nullable=False)
