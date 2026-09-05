"""Government advisory JSON ko schema fields mein map karta hai."""


def adapt(raw: dict) -> dict:
    text = raw.get("advisory_text", raw.get("description", ""))

    return {
        "event_date": raw.get("issued_date", ""),
        "location": raw.get("region", raw.get("location", "")),
        "state": raw.get("state", ""),
        "event_description": text,
        "source_id": f"GOVT_{raw.get('agency', 'NA')}",
        "source_name": raw.get("agency", "government_advisory"),
        "source_type": "Government",
        "source_url": raw.get("url"),
        "published_date": raw.get("issued_date", ""),
        "raw_text": text,
    }