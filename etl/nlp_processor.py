"""
nlp_processor.py
raw_text/event_description se missing fields (event_type, cause, severity,
weather_related, fatalities, injuries, location, state, highway_name)
nikalne ki koshish karta hai — simple keyword-based rules.
YE FILE SAB SOURCES KE LIYE EK JAISI HAI.
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
    "Critical": [
        "closed", "completely blocked", "death", "killed", "fatal",
        "collapse", "collapsed", "washed away", "cut off", "suspended",
        "shut down", "stranded", "destroyed", "devastated",
    ],
    "High": [
        "injured", "injuries", "major damage", "disrupted", "disruption",
        "damaged", "blocked", "severe", "heavy damage",
    ],
    "Medium": [
        "delay", "slow", "restricted", "diversion", "congestion", "affected",
    ],
    "Low": [
        "minor", "resumed", "reopened", "restored", "normal",
    ],
}

SEVERITY_SCORE_MAP = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

# GDACS disaster alerts apna khud ka "Green/Orange/Red" alert level text mein
# deta hai — isse directly severity mein map kar sakte hain (keyword guessing se better)
GDACS_ALERT_TO_SEVERITY = {
    "green": "Low",
    "orange": "High",
    "red": "Critical",
}



# ================================================================
# LOCATION EXTRACTION — Indian states/UTs + major cities/highway hubs
# Isse text se location nikalti hai jab CSV/JSON ka location field khaali ho.
# ================================================================

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Jammu & Kashmir", "Jammu and Kashmir", "Ladakh",
    "Delhi", "Puducherry", "Chandigarh",
]

CITY_TO_STATE = {
    "Mumbai": "Maharashtra", "Pune": "Maharashtra", "Nagpur": "Maharashtra",
    "Nashik": "Maharashtra", "Thane": "Maharashtra",
    "Delhi": "Delhi", "New Delhi": "Delhi",
    "Bengaluru": "Karnataka", "Bangalore": "Karnataka", "Mangaluru": "Karnataka",
    "Mangalore": "Karnataka",
    "Hyderabad": "Telangana",
    "Ahmedabad": "Gujarat", "Surat": "Gujarat", "Vadodara": "Gujarat",
    "Rajkot": "Gujarat",
    "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu", "Madurai": "Tamil Nadu",
    "Trichy": "Tamil Nadu", "Tiruchirappalli": "Tamil Nadu",
    "Kolkata": "West Bengal",
    "Jaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh", "Kanpur": "Uttar Pradesh", "Agra": "Uttar Pradesh",
    "Meerut": "Uttar Pradesh", "Varanasi": "Uttar Pradesh", "Prayagraj": "Uttar Pradesh",
    "Noida": "Uttar Pradesh", "Ghaziabad": "Uttar Pradesh",
    "Indore": "Madhya Pradesh", "Bhopal": "Madhya Pradesh",
    "Patna": "Bihar",
    "Ludhiana": "Punjab", "Amritsar": "Punjab",
    "Srinagar": "Jammu & Kashmir", "Ramban": "Jammu & Kashmir", "Jammu": "Jammu & Kashmir",
    "Kinnaur": "Himachal Pradesh", "Shimla": "Himachal Pradesh",
    "Dehradun": "Uttarakhand",
    "Guwahati": "Assam",
    "Chandigarh": "Chandigarh",
    "Thrissur": "Kerala", "Kochi": "Kerala",
    "Gurugram": "Haryana", "Gurgaon": "Haryana", "Faridabad": "Haryana",
    "Balotra": "Rajasthan",
    "Vijayawada": "Andhra Pradesh",
}

MAJOR_CITIES = list(CITY_TO_STATE.keys())

# NH-44, NH 48, National Highway 8 jaise patterns dhoondti hai
HIGHWAY_NUMBER_PATTERN = re.compile(r"\b(?:NH|SH|National Highway|State Highway)[-\s]?(\d{1,3})\b", re.IGNORECASE)

# "Mumbai-Pune Expressway", "Delhi-Dehradun Expressway", "Jammu-Srinagar National Highway"
# jaise named highways/expressways dhoondti hai (do city names + Expressway/Highway word)
HIGHWAY_NAME_PATTERN = re.compile(
    r"\b([A-Z][a-zA-Z]+(?:-[A-Z][a-zA-Z]+)+)\s+(?:National\s+|State\s+)?(Expressway|Highway)\b"
)

def extract_location_from_text(text: str):
    """
    Text mein se pehli match hui state/city return karta hai.
    Returns: (location, state) tuple — dono None ho sakte hain agar kuch na mile.
    """
    if not text:
        return None, None

    # Pehle cities dhoondo (zyada specific hoti hain) — city mile to uski state bhi mil jaati hai
    for city in MAJOR_CITIES:
        pattern = r"\b" + re.escape(city) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            return city, CITY_TO_STATE.get(city)

    # Fir seedha states dhoondo (agar koi city match nahi hui)
    for state in INDIAN_STATES:
        pattern = r"\b" + re.escape(state) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            return state, state

    return None, None

def extract_highway_from_text(text: str):
    """
    Text mein se highway ka naam nikaalta hai — do tareeke se:
    1. Number wale format se (NH-44, SH-12)
    2. Named format se (Mumbai-Pune Expressway, Jammu-Srinagar National Highway)
    """
    if not text:
        return None

    # Pehle number wala pattern try karo (zyada canonical/precise hota hai)
    number_match = HIGHWAY_NUMBER_PATTERN.search(text)
    if number_match:
        return f"NH-{number_match.group(1)}"

    # Fir named highway/expressway pattern try karo
    name_match = HIGHWAY_NAME_PATTERN.search(text)
    if name_match:
        return f"{name_match.group(1)} {name_match.group(2)}"

    return None

def detect_from_keywords(text: str, keyword_map: dict):
    text_lower = text.lower()
    for label, keywords in keyword_map.items():
        for kw in keywords:
            if kw in text_lower:
                return label
    return None

def extract_gdacs_alert_severity(text: str):
    """
    GDACS disaster text mein 'Green earthquake', 'Orange notification',
    'Red alert' jaisa pattern hota hai — ye seedha alert level batata hai
    jo keyword-guessing se zyada reliable hai.
    """
    if not text:
        return None
    text_lower = text.lower()
    for level, severity in GDACS_ALERT_TO_SEVERITY.items():
        if level in text_lower[:30]:  # alert level hamesha text ke shuru mein hota hai
            return severity
    return None


def extract_number_near_word(text: str, word: str):
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
        # Pehle GDACS alert level try karo (Disaster source ke liye zyada reliable)
        detected = extract_gdacs_alert_severity(text)
        if not detected:
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

    # Location aur state text se extract karo (agar pehle se khaali hain)
    if not record.get("location"):
        location, state = extract_location_from_text(text)
        if location:
            record["location"] = location
        if state and not record.get("state"):
            record["state"] = state

    # Highway name text se extract karo
    if not record.get("highway_name"):
        highway = extract_highway_from_text(text)
        if highway:
            record["highway_name"] = highway

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