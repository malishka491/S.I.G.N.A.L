"""
government_collector.py
Google News RSS se government/NHAI/traffic advisories fetch karta hai.
(PIB ka direct RSS blocked/unreliable tha, isliye ye proven method use kar rahe hain —
same jaisa news_collector.py mein kaam kar raha hai.)
"""

import feedparser
import json
import os
import time
from datetime import datetime, timezone
from ingestion.utils.logger_config import get_logger

logger = get_logger(__name__)

RAW_DATA_DIR = os.path.join("data", "raw", "government")

SEARCH_QUERIES = [
    "government advisory highway India",
    "NHAI advisory road closure",
    "traffic advisory government India",
]


def build_rss_url(query: str) -> str:
    encoded_query = query.replace(" ", "+")
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"


def fetch_advisories_for_query(query: str) -> list:
    url = build_rss_url(query)
    feed = feedparser.parse(url)
    return feed.entries


def save_advisory(entry, index: int):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"govt_{timestamp_str}_{index}.json"
    filepath = os.path.join(RAW_DATA_DIR, filename)

    title_parts = entry.get("title", "").rsplit(" - ", 1)
    title = title_parts[0]
    agency = title_parts[1] if len(title_parts) > 1 else "Government Source"

    record = {
        "advisory_text": f"{title}. {entry.get('summary', '')}",
        "region": "",
        "state": "",
        "issued_date": entry.get("published", ""),
        "agency": agency,
        "url": entry.get("link", ""),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)


def collect_government_advisories():
    index = 0
    for query in SEARCH_QUERIES:
        entries = fetch_advisories_for_query(query)
        logger.info(f"Fetched {len(entries)} advisories for query '{query}'")

        for entry in entries:
            save_advisory(entry, index)
            index += 1

        time.sleep(1)

    logger.info(f"Saved {index} advisory files total")


if __name__ == "__main__":
    logger.info("=== Government Collector Started ===")
    collect_government_advisories()
    logger.info("=== Government Collector Finished ===")