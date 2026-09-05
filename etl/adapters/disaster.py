"""Weather/Disaster alert JSON ko schema fields mein map karta hai."""


def adapt(raw: dict) -> dict:
    text = raw.get("alert_text", raw.get("description", ""))

    return {
        "event_date": raw.get("alert_date", raw.get("issued_date", "")),
        "location": raw.get("area", raw.get("location", "")),
        "event_description": text,
        "weather_related": "Yes",
        "source_id": f"DIS_{raw.get('agency', 'NA')}",
        "source_name": raw.get("agency", "disaster_alert"),
        "source_type": "Disaster",
        "source_url": raw.get("url"),
        "published_date": raw.get("alert_date", ""),
        "raw_text": text,
    }