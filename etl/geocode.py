"""
geocode.py
location_name ko latitude/longitude mein convert karta hai — OpenStreetMap
Nominatim (free) API use karke. Result CACHE hota hai taaki same location
baar-baar API call na kare.
"""

import requests
import time
from etl.utils.logger_config import get_logger

logger = get_logger(__name__)

_CACHE = {}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "SIGNAL-RoadRiskProject/1.0"}


def geocode_location(location_name: str, state: str = ""):
    if not location_name:
        return None, None

    query = f"{location_name}, {state}, India" if state else f"{location_name}, India"

    if query in _CACHE:
        return _CACHE[query]

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": query, "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        results = response.json()

        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            _CACHE[query] = (lat, lon)
            time.sleep(1)
            return lat, lon
        else:
            logger.warning(f"Geocode nahi mila: {query}")
            return None, None

    except requests.exceptions.RequestException as err:
        logger.error(f"Geocoding error for '{query}': {err}")
        return None, None


def geocode_records(records: list) -> list:
    for record in records:
        if record.get("latitude") and record.get("longitude"):
            continue

        location = record.get("location", "")
        state = record.get("state", "")
        if location:
            lat, lon = geocode_location(location, state)
            record["latitude"] = lat
            record["longitude"] = lon

    logger.info(f"Geocoded {len(records)} records")
    return records


if __name__ == "__main__":
    from etl.extract import extract_all_sources
    from etl.clean import clean_records
    from etl.nlp_processor import enrich_records

    raw = extract_all_sources()
    cleaned = clean_records(raw)
    enriched = enrich_records(cleaned)
    geocoded = geocode_records(enriched)

    print(f"\nTotal geocoded records: {len(geocoded)}")
    if geocoded:
        print("\nSample geocoded record:")
        print(geocoded[0])