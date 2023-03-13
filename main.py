from config import Config
import logging
from nubank import NubankExtractor
from db_manager import NubankDbManager

config = Config()
config.logging_config()
nubank_db_manager = NubankDbManager()
nubank_extractor = NubankExtractor(
    config.user_id, config.password, config.cert_path, nubank_db_manager
)

logging.info("Starting card statements import")
nubank_extractor.extract_nubank_data()
