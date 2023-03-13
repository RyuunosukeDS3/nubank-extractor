from .models import CardTransactions

from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import CardTransactions, AccountTransactions


class NubankDbManager(object):
    def __init__(self):
        config = Config()
        engine = create_engine(config.db_uri)
        Session = sessionmaker(bind=engine)
        self.session = Session()

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
                source=transaction["source"],
                target=transaction["target"],
                amount=transaction["amount"],
                time=transaction["time"],
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
