"""Weather API raw JSON ko schema fields mein map karta hai."""


def adapt(raw: dict) -> dict:
    current = raw.get("raw_response", {}).get("current", {})
    metadata = raw.get("metadata", {})

    return {
        "event_date": metadata.get("collection_time_utc", ""),
        "location": metadata.get("location_name", ""),
        "weather_condition": None,
        "temperature": current.get("temperature_2m"),
        "rainfall_mm": current.get("precipitation"),
        "wind_speed": current.get("wind_speed_10m"),
        "weather_related": "Yes",
        "source_id": f"WTHR_{metadata.get('location_name', 'NA')}",
        "source_name": metadata.get("source", "weather_api"),
        "source_type": "Weather",
        "source_url": None,
        "published_date": metadata.get("collection_time_utc", ""),
        "raw_text": "",
    }