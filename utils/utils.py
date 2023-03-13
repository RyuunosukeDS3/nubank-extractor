from datetime import datetime


@staticmethod
def format_time(time):
    for format in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            time = datetime.strptime(time, format)
        except Exception:
            pass

    return time
