# pylint: disable=singleton-comparison
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from .models import CardTransactions, AccountTransactions


class NubankDbManager:
    def __init__(self):
        config = Config()
        engine = create_engine(config.db_uri)
        session = sessionmaker(bind=engine)
        self.session = session()

    def save_card_transaction(self, transaction):
        self.session.add(
            CardTransactions(
                id=transaction["id"],
                description=transaction["description"],
                title=transaction["title"],
                amount=transaction["amount"],
                time=transaction["time"],
                charges=transaction["charges"],
                charge_amount=transaction["charge_amount"],
            )
        )
        self.session.commit()

    def save_account_transaction(self, transaction):
        self.session.add(
            AccountTransactions(
                id=transaction["id"],
                payment_type=transaction["payment_type"],
                type=transaction["type"],
                endpoint=transaction["endpoint"],
                time=transaction["time"],
                amount=transaction["amount"],
            )
        )
        self.session.commit()

    def card_statement_exists(self, transaction_id):
        return (
            self.session.query(CardTransactions)
            .filter(CardTransactions.id == transaction_id)
            .first()
        )

    def set_paid_as_true(self, transaction_id):
        self.session.query(CardTransactions).filter(
            CardTransactions.id == transaction_id
        ).update({"paid": True})
        self.session.commit()

    def get_ongoing_payments_in_installments(self):
        return (
            self.session.query(CardTransactions)
            .filter(CardTransactions.charges != None, CardTransactions.settled == False)
            .all()
        )

    def update_remaining_charges(self, transaction_id, paid, remaining_charges):
        self.session.query(CardTransactions).filter(
            CardTransactions.id == transaction_id
        ).update({"paid": paid, "remaining_charges": remaining_charges})
        self.session.commit()

    def account_statement_exists(self, transaction_id):
        return (
            self.session.query(AccountTransactions)
            .filter(AccountTransactions.id == transaction_id)
            .first()
        )

    def get_unpaid_card_statements(self):
        return (
            self.session.query(CardTransactions)
            .filter(CardTransactions.paid == False)
            .all()
        )
