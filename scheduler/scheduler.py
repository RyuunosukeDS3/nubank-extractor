import time
import logging
import schedule
from db_manager import NubankDbManager
from nubank import NubankExtractor
from config import Config


class ScheduleJob:
    def __init__(self):
        self.config = Config()
        nubank_db_manager = NubankDbManager()
        self.nubank_extractor = NubankExtractor(
            self.config.user_id,
            self.config.password,
            self.config.cert_path,
            nubank_db_manager,
        )

    def extract_nubank_data(self):
        logging.info("Starting to run nubank extraction")
        self.nubank_extractor.get_and_navigate_through_card_statements()
        self.nubank_extractor.check_if_is_fully_paid()
        self.nubank_extractor.get_and_navigate_through_account_statements()
        logging.info("Finished running extraction")

    def run_jobs(self):
        self.extract_nubank_data()
        logging.info(
            "Scheduling job %s to run everyday at %s UTC",
            self.extract_nubank_data.__name__,
            self.config.run_time,
        )

        schedule.every().day.at(self.config.run_time).do(self.extract_nubank_data)
        while True:
            schedule.run_pending()
            time.sleep(60)
