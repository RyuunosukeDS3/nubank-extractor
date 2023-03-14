import argparse
from config import Config
from scheduler import ScheduleJob


parser = argparse.ArgumentParser()
config = Config()
config.logging_config()
schedule_job = ScheduleJob()

parser.add_argument(
    "-sr",
    "--single-run",
    dest="single_run",
    default=False,
    help="Run extraction once",
)
args = parser.parse_args()

if args.single_run:
    schedule_job.extract_nubank_data()

else:
    schedule_job.run_jobs()
