import schedule
import time
from db_manager import NubankDbManager
from nubank import NubankExtractor
from config import Config


class ScheduleJob(object):
    def __init__(self):
        config = Config()
        nubank_db_manager = NubankDbManager()
        self.nubank_extractor = NubankExtractor(
            config.user_id, config.password, config.cert_path, nubank_db_manager
        )

    def extract_nubank_data(self):
        self.nubank_extractor.get_and_navigate_through_card_statements()
        self.nubank_extractor.check_if_is_fully_paid()
        self.nubank_extractor.get_and_navigate_through_account_statements()

    def run_jobs(self):
        schedule.every().day.at("20:52").do(self.extract_nubank_data)
        while True:
            schedule.run_pending()
            time.sleep(60)
