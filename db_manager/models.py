from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, TIMESTAMP, Boolean, Integer

Base = declarative_base()
metadata = Base.metadata


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


class AccountTransactions(Base):
    __tablename__ = "account_transactions"

    id = Column(String(255), primary_key=True)
    payment_type = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)
    endpoint = Column(String(255), nullable=False)
    time = Column(TIMESTAMP, nullable=False)
    amount = Column(Integer(), nullable=False)
