from datetime import datetime
import easyocr

reader = easyocr.Reader(['fr'], gpu=False)


def timestamp_to_date(s):
    if s is not None:
        return datetime.utcfromtimestamp(s)
    return None


def extract_text(image_url):
    try:
        RST = reader.readtext(image_url)
        result = ""
        for r in RST:
            text = r[1]
            confidence = r[2]
            if confidence >= 0.5:
                result += f"{text} "
        return None if (result == "") else result.strip()
    except Exception as e:
        traceback.print_exc()
        return None
