"""News CSV row ko schema fields mein map karta hai."""


def adapt(row: dict) -> dict:
    title = row.get("title", "")
    summary = row.get("summary", "")

    return {
        "event_date": row.get("date", ""),
        "location": row.get("location", ""),
        "highway_name": row.get("route", ""),
        "cause": row.get("cause", ""),
        "event_description": f"{title}. {summary}".strip(),
        "road_damage": "Yes" if row.get("damage") else None,
        "source_id": f"NEWS_{hash(row.get('link',''))}",
        "source_name": row.get("source", "news_portal"),
        "source_type": "News",
        "source_url": row.get("link", ""),
        "published_date": row.get("date", ""),
        "raw_text": f"{title}. {summary}",
    }