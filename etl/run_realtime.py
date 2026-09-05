"""
run_realtime.py

Connects Maahi's existing collector to Malishka's ETL pipeline.
Processes only the newly collected CSV file.
"""

import os
import glob

from ingestion.news.news_collector import collect_all_queries
from etl.pipeline import run_pipeline


NEWS_FOLDER = os.path.join("data", "raw", "news")


def run_realtime():

    print("=== REAL-TIME CONNECTOR STARTED ===")

    # Remember existing CSV files
    before_files = set(
        glob.glob(
            os.path.join(NEWS_FOLDER, "**", "*.csv"),
            recursive=True
        )
    )

    # 1. Maahi's collector fetches fresh news
    print("Fetching fresh news...")
    collect_all_queries()

    # 2. Find only the newly created CSV file
    after_files = set(
        glob.glob(
            os.path.join(NEWS_FOLDER, "**", "*.csv"),
            recursive=True
        )
    )

    new_files = list(after_files - before_files)

    if not new_files:
        print("No new news file found. ETL stopped.")
        return

    print(f"New file found: {new_files[0]}")

    # 3. Process only the fresh CSV
    print("Running ETL pipeline...")
    events = run_pipeline(
        use_geocoding=True,
        selected_files=[("news", new_files[0])]
    )

    print(
        f"=== REAL-TIME CONNECTOR FINISHED — "
        f"{len(events)} events ==="
    )


if __name__ == "__main__":
    run_realtime()