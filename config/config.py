from os import getenv
from dotenv import load_dotenv
import logging


class Config(object):
    def __init__(self):
        load_dotenv()

        self.user_id = getenv("CPF")
        self.password = getenv("PASSWORD")
        self.cert_path = getenv("CERT_PATH")
        self.db_uri = getenv("DB_URI")

    @staticmethod
    def logging_config():
        logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=logging.INFO,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
