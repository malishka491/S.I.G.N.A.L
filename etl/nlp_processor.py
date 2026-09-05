"""
nlp_processor.py
raw_text/event_description se missing fields (event_type, cause, severity,
weather_related, fatalities, injuries) nikalne ki koshish karta hai —
simple keyword-based rules. YE FILE SAB SOURCES KE LIYE EK JAISI HAI.
"""

import re
from etl.utils.logger_config import get_logger

logger = get_logger(__name__)

EVENT_TYPE_KEYWORDS = {
    "Accident": ["accident", "collision", "crash"],
    "Landslide": ["landslide", "mudslide"],
    "Flood": ["flood", "flooding", "waterlogged"],
    "Road blockage": ["blocked", "blockage", "closed road"],
    "Traffic jam": ["traffic jam", "congestion", "gridlock"],
    "Vehicle breakdown": ["breakdown", "stalled vehicle"],
    "Road construction": ["construction", "roadwork"],
    "Fire": ["fire", "blaze", "forest fire"],
    "Snowfall": ["snowfall", "snow"],
    "Avalanche": ["avalanche"],
    "Rockfall": ["rockfall", "boulder"],
    "Bridge damage": ["bridge collapse", "bridge damage"],
    "Road closure": ["highway closed", "road closed"],
    "Earthquake": ["earthquake"],
    "Cyclone": ["cyclone", "hurricane", "typhoon", "tropical storm"],
    "Drought": ["drought"],
    "Volcanic Eruption": ["volcanic", "volcano", "eruption"],
    "Other": [],
}

CAUSE_KEYWORDS = {
    "Heavy rain": ["heavy rain", "rainfall", "downpour"],
    "Flood": ["flood"],
    "Landslide": ["landslide"],
    "Snowfall": ["snow"],
    "Avalanche": ["avalanche"],
    "Poor road condition": ["poor road", "pothole"],
    "Overspeeding": ["overspeeding", "speeding"],
    "Vehicle failure": ["vehicle failure", "brake fail"],
    "Construction": ["construction"],
}

SEVERITY_KEYWORDS = {
    "Critical": ["closed", "completely blocked", "death", "killed", "fatal"],
    "High": ["injured", "injuries", "major damage"],
    "Medium": ["delay", "slow"],
    "Low": ["minor"],
}

SEVERITY_SCORE_MAP = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}


def detect_from_keywords(text: str, keyword_map: dict):
    text_lower = text.lower()
    for label, keywords in keyword_map.items():
        for kw in keywords:
            if kw in text_lower:
                return label
    return None


def extract_number_near_word(text: str, word: str):
    """'2 people injured' jaise text se number nikalta hai."""
    pattern = rf"(\d+)\s+(?:people\s+)?{word}"
    match = re.search(pattern, text.lower())
    return int(match.group(1)) if match else None


def enrich_record(record: dict) -> dict:
    text = record.get("raw_text") or record.get("event_description") or ""
    if not text:
        return record

    if not record.get("event_type"):
        detected = detect_from_keywords(text, EVENT_TYPE_KEYWORDS)
        if detected:
            record["event_type"] = detected

    if not record.get("cause"):
        detected = detect_from_keywords(text, CAUSE_KEYWORDS)
        if detected:
            record["cause"] = detected

    if not record.get("severity"):
        detected = detect_from_keywords(text, SEVERITY_KEYWORDS)
        if detected:
            record["severity"] = detected
            record["severity_score"] = SEVERITY_SCORE_MAP.get(detected)

    if not record.get("weather_related"):
        weather_words = ["rain", "flood", "snow", "storm", "fog", "avalanche"]
        record["weather_related"] = "Yes" if any(w in text.lower() for w in weather_words) else "No"

    if not record.get("injuries"):
        record["injuries"] = extract_number_near_word(text, "injured")

    if not record.get("fatalities"):
        record["fatalities"] = extract_number_near_word(text, "killed")

    return record


def enrich_records(records: list) -> list:
    enriched = [enrich_record(r) for r in records]
    logger.info(f"NLP-enriched {len(enriched)} records")
    return enriched


if __name__ == "__main__":
    from etl.extract import extract_all_sources
    from etl.clean import clean_records

    raw = extract_all_sources()
    cleaned = clean_records(raw)
    enriched = enrich_records(cleaned)

    print(f"\nTotal enriched records: {len(enriched)}")
    if enriched:
        print("\nSample enriched record:")
        print(enriched[0])