from datetime import datetime
import unidecode
from typing import List
from models import ad_status_model


def timestamp_to_date(s):
    if s is not None:
        return datetime.utcfromtimestamp(s)
    return None


def analyse_ad_status(text, keywords_bad: List[str], keywords_hidden: List[str], keywords_incorrect: List[str]):
    if text:
        if any(s in unidecode.unidecode(text.lower()) for s in keywords_incorrect):
            return ad_status_model.AD_STATUS_INCORRECT
        if any(s in unidecode.unidecode(text.lower()) for s in keywords_bad):
            return ad_status_model.AD_STATUS_BAD
        if any(s in unidecode.unidecode(text.lower()) for s in keywords_hidden):
            return ad_status_model.AD_STATUS_HIDDEN
    return 0
