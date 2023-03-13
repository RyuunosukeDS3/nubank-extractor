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

    def extract_nubank_data(self):
        # self._get_and_navigate_through_card_statements()
        self._get_and_navigate_through_account_statements()

    def _get_and_navigate_through_card_statements(self):
        statements = self.nubank.get_card_statements()
        for statement in statements:
            existing_transaction = self.nubank_db_manager.card_statement_exists(
                statement["id"]
            )
            if existing_transaction:
                self._is_fully_paid(existing_transaction)
            else:
                self._save_card_statements(statement)

    def _save_card_statements(self, statement):
        paid = False
        time = format_time(statement["time"])

        charges = 1
        charge_amount = statement["amount"]

        logging.info(
            "Saving transaction %s with name %s",
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

    def _is_fully_paid(self, existing_transaction):
        if existing_transaction.paid == False:
            paied_bills = self._get_paied_bills(existing_transaction.time)
            paid = False

            remaining_charges = (
                existing_transaction.charges - (paied_bills)
                if existing_transaction.charges - (paied_bills) > 0
                else 0
            )
            if remaining_charges >= 0:
                logging.info(
                    "Updating transaction %s with name %s",
                    existing_transaction.id,
                    existing_transaction.description,
                )
                self.nubank_db_manager.set_paid_as_true(existing_transaction.id)

                if remaining_charges == 0:
                    paid = True

                self.nubank_db_manager.update_remaining_charges(
                    existing_transaction.id, paid, remaining_charges
                )

    @staticmethod
    def _get_paied_bills(date):
        date = date.replace(day=5)
        if not date.tzinfo:
            date = UTC.localize(date)
        delta = relativedelta.relativedelta(UTC.localize(datetime.now()), date)
        return delta.months + delta.years * 12

    def get_account_statements(self):
        return self.nubank.get_account_statements()

    def _get_and_navigate_through_account_statements(self):
        statements = self.nubank.get_account_statements_paginated()

        while len(statements["edges"]) > 0:
            for statement in statements["edges"]:
                if (
                    not statement["node"]["footer"]
                    or "Valor adicionado na conta por cartão de crédito e enviado por Pix"
                    not in statement["node"]["footer"]
                ):
                    if "money-out" in statement["node"]["tags"]:
                        payment_type = "made"

                    elif "money-in" in statement["node"]["tags"]:
                        payment_type = "reicived"

                    if "Compra no débito" in statement["node"]["title"]:
                        type = "debit card"

                    elif "Transferência" in statement["node"]["title"]:
                        if statement["node"]["footer"] == "Pix":
                            type = "pix"
                        else:
                            type = "transfer"
                    else:
                        if "payments" in statement["node"]["tags"]:
                            type = "payment"
                            if "Pagamento da fatura" in statement["node"]["title"]:
                                target = "nu credit card"
                            else:
                                target = statement["node"]["detail"].split("\n")[0]

                    transacion = {
                        "id": statement["node"]["id"],
                        "payment_type": payment_type,
                        "type": type,
                        "target": target,
                    }

            cursor = statements["edges"][-1]["cursor"]
            statements = self.nubank.get_account_statements_paginated(cursor)
