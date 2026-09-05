"""
disaster_collector.py
GDACS se real disaster alerts fetch karta hai (floods, cyclones, earthquakes).
"""

import feedparser
import json
import os
from datetime import datetime, timezone
from ingestion.utils.logger_config import get_logger

logger = get_logger(__name__)

RAW_DATA_DIR = os.path.join("data", "raw", "disaster")
GDACS_RSS_URL = "https://www.gdacs.org/xml/rss.xml"


def fetch_disaster_alerts() -> list:
    feed = feedparser.parse(GDACS_RSS_URL)
    return feed.entries


def save_alert(entry, index: int):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"disaster_{timestamp_str}_{index}.json"
    filepath = os.path.join(RAW_DATA_DIR, filename)

    record = {
        "alert_text": f"{entry.get('title', '')}. {entry.get('summary', '')}",
        "area": "",
        "alert_date": entry.get("published", ""),
        "agency": "GDACS",
        "url": entry.get("link", ""),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)


def collect_disaster_alerts():
    entries = fetch_disaster_alerts()
    logger.info(f"Fetched {len(entries)} disaster alerts from GDACS")

    for i, entry in enumerate(entries):
        save_alert(entry, i)

    logger.info(f"Saved {len(entries)} disaster alert files")


if __name__ == "__main__":
    logger.info("=== Disaster Collector Started ===")
    collect_disaster_alerts()
    logger.info("=== Disaster Collector Finished ===")