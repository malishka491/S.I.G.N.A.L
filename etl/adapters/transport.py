"""Police/Transport notice JSON ko schema fields mein map karta hai."""


def adapt(raw: dict) -> dict:
    text = raw.get("notice_text", raw.get("description", ""))

    return {
        "event_date": raw.get("notice_date", ""),
        "location": raw.get("location", ""),
        "highway_name": raw.get("route", ""),
        "event_description": text,
        "source_id": f"TRNS_{raw.get('department', 'NA')}",
        "source_name": raw.get("department", "transport_notice"),
        "source_type": "Transport",
        "source_url": raw.get("url"),
        "published_date": raw.get("notice_date", ""),
        "raw_text": text,
    }