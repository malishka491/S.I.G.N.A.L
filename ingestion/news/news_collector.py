"""
news_collector.py
Google News RSS se highway/accident related news fetch karta hai.
"""

import feedparser
import csv
import os
import time
from datetime import datetime, timezone
from ingestion.utils.logger_config import get_logger

logger = get_logger(__name__)

RAW_DATA_DIR = os.path.join("data", "raw", "news")

SEARCH_QUERIES = [
    "highway accident India",
    "landslide highway India",
    "flood road blocked India",
]


def build_rss_url(query: str) -> str:
    encoded_query = query.replace(" ", "+")
    return f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"


def fetch_news_for_query(query: str) -> list:
    url = build_rss_url(query)
    feed = feedparser.parse(url)

    rows = []
    for entry in feed.entries:
        title_parts = entry.title.rsplit(" - ", 1)
        title = title_parts[0]
        source_name = title_parts[1] if len(title_parts) > 1 else "Unknown"

        rows.append({
            "date": entry.get("published", ""),
            "location": "",
            "route": "",
            "cause": "",
            "damage": "",
            "title": title,
            "summary": entry.get("summary", ""),
            "source": source_name,
            "link": entry.get("link", ""),
        })
    return rows


def save_to_csv(rows: list):
    if not rows:
        logger.warning("Koi news rows nahi mile.")
        return

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    filepath = os.path.join(RAW_DATA_DIR, f"news_{timestamp_str}.csv")

    fieldnames = ["date", "location", "route", "cause", "damage", "title", "summary", "source", "link"]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    logger.info(f"Saved {len(rows)} news rows to {filepath}")


def collect_all_queries():
    all_rows = []
    for query in SEARCH_QUERIES:
        logger.info(f"Fetching news for query: '{query}'")
        rows = fetch_news_for_query(query)
        all_rows.extend(rows)
        time.sleep(1)

    save_to_csv(all_rows)


if __name__ == "__main__":
    logger.info("=== News Collector Started ===")
    collect_all_queries()
    logger.info("=== News Collector Finished ===")