from config import Config
from scheduler import ScheduleJob

config = Config()
config.logging_config()
schedule_job = ScheduleJob()
schedule_job.run_jobs()
