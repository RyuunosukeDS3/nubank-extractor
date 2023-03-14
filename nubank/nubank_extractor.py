from pynubank import Nubank
import logging
from utils import format_time
from dateutil import relativedelta
from datetime import datetime
from pytz import UTC


class NubankExtractor(object):
    def __init__(self, user_id, password, cert_path, nubank_db_manager):
        self.nubank = Nubank()
        self.nubank.authenticate_with_cert(user_id, password, cert_path)
        self.nubank_db_manager = nubank_db_manager

    def get_and_navigate_through_card_statements(self):
        """Require nubank card data and navigate through it"""
        try:
            statements = self.nubank.get_card_statements()
            for statement in statements:
                existing_transaction = self.nubank_db_manager.card_statement_exists(
                    statement["id"]
                )
                if not existing_transaction:
                    self._save_card_statements(statement)
        except Exception as err:
            logging.error(err)

    def _save_card_statements(self, statement):
        paid = False
        time = format_time(statement["time"])

        charges = 1
        charge_amount = statement["amount"]

        logging.info(
            "Saving card transaction %s with name %s",
            statement["id"],
            statement["description"],
        )

        if "charges" in statement["details"]:
            charges = statement["details"]["charges"]["count"]
            charge_amount = statement["details"]["charges"]["amount"]

            if self._get_paied_bills(time) >= statement["details"]["charges"]["count"]:
                paid = True

        transaction = {
            "id": statement["id"],
            "description": statement["description"],
            "title": statement["title"],
            "amount": statement["amount"],
            "time": time,
            "charges": charges,
            "charge_amount": charge_amount,
            "remaining_amount": statement["amount"],
            "paid": paid,
        }

        self.nubank_db_manager.save_card_transaction(transaction)

    def check_if_is_fully_paid(self):
        """Check if installments are fully paid"""
        try:
            unpaid_statemens = self.nubank_db_manager.get_unpaid_card_statements()

            for transaction in unpaid_statemens:
                if transaction.paid == False:
                    paied_bills = self._get_paied_bills(transaction.time)
                    paid = False

                    remaining_charges = (
                        transaction.charges - (paied_bills)
                        if transaction.charges - (paied_bills) > 0
                        else 0
                    )
                    if remaining_charges >= 0:
                        logging.info(
                            "Updating card transaction %s with name %s",
                            transaction.id,
                            transaction.description,
                        )
                        self.nubank_db_manager.set_paid_as_true(transaction.id)

                        if remaining_charges == 0:
                            paid = True

                        self.nubank_db_manager.update_remaining_charges(
                            transaction.id, paid, remaining_charges
                        )
        except Exception as err:
            logging.error(err)

    @staticmethod
    def _get_paied_bills(date):
        date = date.replace(day=5)
        # pylint: disable=no-value-for-parameter
        if not date.tzinfo:
            date = UTC.localize(date)
        delta = relativedelta.relativedelta(UTC.localize(datetime.now()), date)
        # pylint: enable=no-value-for-parameter
        return delta.months + delta.years * 12

    def get_and_navigate_through_account_statements(self):
        """Require nubank account data and navigate through it"""
        try:
            statements = self.nubank.get_account_statements_paginated()

            while len(statements["edges"]) > 0:
                for statement in statements["edges"]:
                    if not self.nubank_db_manager.account_statement_exists(
                        statement["node"]["id"]
                    ):
                        logging.info(
                            "Saving account transaction %s with name %s",
                            statement["node"]["id"],
                            statement["node"]["detail"].split("\n")[0],
                        )

                        self._save_account_statements(statement)

                cursor = statements["edges"][-1]["cursor"]
                statements = self.nubank.get_account_statements_paginated(cursor)
        except Exception as err:
            logging.error(err)

    def _save_account_statements(self, statement):
        transaction = {}

        if (
            not statement["node"]["footer"]
            or "Valor adicionado na conta por cartão de crédito e enviado por Pix"
            not in statement["node"]["footer"]
        ):
            self._allocate_transaction_data(statement, transaction)

            transaction.update(
                {
                    "id": statement["node"]["id"],
                    "time": statement["node"]["postDate"],
                    "amount": statement["node"]["amount"] * 10,
                }
            )

            self.nubank_db_manager.save_account_transaction(transaction)

    def _allocate_transaction_data(self, statement, transaction):
        endpoint = statement["node"]["detail"].split("\n")[0]

        payment_type = self._get_payment_type(statement)
        transaction_type = self._get_type_of_transaction(statement)

        if (
            transaction_type in "payment"
            and "Pagamento da fatura" in statement["node"]["title"]
        ):
            endpoint = "nu credit card"

        transaction.update(
            {
                "payment_type": payment_type,
                "type": transaction_type,
                "endpoint": endpoint,
            }
        )

    def _get_payment_type(self, statement):
        if statement["node"]["tags"]:
            if "money-out" in statement["node"]["tags"]:
                payment_type = "made"

            elif "money-in" in statement["node"]["tags"]:
                payment_type = "recieved"

        else:
            if statement["node"]["kind"] and "POSITIVE" in statement["node"]["kind"]:
                payment_type = "recieved"
            else:
                payment_type = "made"

        return payment_type

    def _get_type_of_transaction(self, statement):
        if "Compra no débito" in statement["node"]["title"]:
            transaction_type = "debit card"

        elif statement["node"]["title"] in ["Estorno de débito", "Reembolso recebido"]:
            transaction_type = "refund"

        elif "Dinheiro resgatado" in statement["node"]["title"]:
            transaction_type = "savings withdraw"

        elif "Dinheiro guardado" in statement["node"]["title"]:
            transaction_type = "savings advance"

        elif (
            "Transferência" in statement["node"]["title"]
            or "Depósito" in statement["node"]["title"]
        ):
            if statement["node"]["footer"] == "Pix":
                transaction_type = "pix"
            else:
                transaction_type = "transfer"
        else:
            if statement["node"]["tags"] and "payments" in statement["node"]["tags"]:
                transaction_type = "payment"

        return transaction_type
