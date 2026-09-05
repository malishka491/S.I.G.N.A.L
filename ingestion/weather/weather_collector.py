"""
weather_collector.py
Open-Meteo API se weather data fetch karke Member 2 ke adapter format mein save karta hai.
"""

import requests
import json
import os
from datetime import datetime, timezone
from ingestion.utils.logger_config import get_logger

logger = get_logger(__name__)

BASE_URL = "https://api.open-meteo.com/v1/forecast"
RAW_DATA_DIR = os.path.join("data", "raw", "weather")

LOCATIONS = [
    {"name": "Kanpur", "lat": 26.4499, "lon": 80.3319},
    {"name": "Ramban", "lat": 33.2433, "lon": 75.2422},
    {"name": "Dehradun", "lat": 30.3165, "lon": 78.0322},
]


def fetch_weather_data(latitude: float, longitude: float) -> dict | None:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        logger.error(f"Weather API error: {err}")
        return None


def save_weather_record(data: dict, location_name: str):
    if data is None:
        return

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    collection_time = datetime.now(timezone.utc)
    timestamp_str = collection_time.strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"weather_{location_name.lower()}_{timestamp_str}.json"
    filepath = os.path.join(RAW_DATA_DIR, filename)

    record = {
        "metadata": {
            "source": "open-meteo",
            "location_name": location_name,
            "collection_time_utc": collection_time.isoformat(),
        },
        "raw_response": data,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved weather data: {filepath}")


def collect_all_locations():
    for loc in LOCATIONS:
        data = fetch_weather_data(loc["lat"], loc["lon"])
        save_weather_record(data, loc["name"])


if __name__ == "__main__":
    logger.info("=== Weather Collector Started ===")
    collect_all_locations()
    logger.info("=== Weather Collector Finished ===")