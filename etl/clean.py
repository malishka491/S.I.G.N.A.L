"""
clean.py
Kisi bhi source se aaye record ko clean karta hai — text trim, date format,
numbers convert. YE FILE SAB SOURCES KE LIYE EK JAISI HAI.
"""

import re
from datetime import datetime
from etl.utils.logger_config import get_logger

logger = get_logger(__name__)

DATE_FIELDS = {"event_date", "published_date"}
INT_FIELDS = {"fatalities", "injuries", "vehicles_involved", "vehicles_affected",
              "delay_minutes", "severity_score"}
FLOAT_FIELDS = {"latitude", "longitude", "rainfall_mm", "visibility_km", "temperature"}


def clean_text(value) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    value = value.replace("&nbsp;", " ").replace("&amp;", "&")
    return value


def clean_date(value) -> str:
    if not value:
        return ""
    value = str(value).strip()

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        pass

    for fmt in [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%d %B %Y",
        "%a, %d %b %Y %H:%M:%S %Z",   # RSS format: "Fri, 28 Aug 2026 23:06:53 GMT"
        "%a, %d %b %Y %H:%M:%S %z",   # Kabhi kabhi timezone offset ke saath aata hai
    ]:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    logger.warning(f"Date parse nahi hui: '{value}'")
    return ""

def clean_number(value, to_type):
    if value in (None, ""):
        return None
    try:
        cleaned = re.sub(r"[^\d.\-]", "", str(value))
        return to_type(cleaned) if cleaned else None
    except ValueError:
        return None


def clean_record(record: dict) -> dict:
    cleaned = {}
    for key, value in record.items():
        if key in DATE_FIELDS:
            cleaned[key] = clean_date(value)
        elif key in INT_FIELDS:
            cleaned[key] = clean_number(value, int)
        elif key in FLOAT_FIELDS:
            cleaned[key] = clean_number(value, float)
        elif isinstance(value, str):
            cleaned[key] = clean_text(value)
        else:
            cleaned[key] = value
    return cleaned


def clean_records(records: list) -> list:
    cleaned = [clean_record(r) for r in records]
    logger.info(f"Cleaned {len(cleaned)} records")
    return cleaned


if __name__ == "__main__":
    from etl.extract import extract_all_sources

    raw_records = extract_all_sources()
    cleaned_records = clean_records(raw_records)

    print(f"\nTotal cleaned records: {len(cleaned_records)}")
    if cleaned_records:
        print("\nSample cleaned record:")
        print(cleaned_records[0])