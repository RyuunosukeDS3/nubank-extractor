import logging
from os import getenv
from dotenv import load_dotenv


class Config:
    def __init__(self):
        load_dotenv()

        self.user_id = getenv("CPF")
        self.password = getenv("PASSWORD")
        self.cert_path = getenv("CERT_PATH")
        self.db_uri = getenv("DB_URI")
        self.run_time = int(getenv("RUN_TIME"))

    @staticmethod
    def logging_config():
        logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=logging.INFO,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
