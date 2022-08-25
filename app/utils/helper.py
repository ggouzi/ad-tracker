from datetime import datetime


def timestamp_to_date(s):
    if s is not None:
        return datetime.utcfromtimestamp(s)
    return None
