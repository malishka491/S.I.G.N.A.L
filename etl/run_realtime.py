"""
run_realtime.py

Connects Maahi's existing collector to Malishka's ETL pipeline.
Does not modify the collector code.
"""

from ingestion.news.news_collector import collect_all_queries
from etl.pipeline import run_pipeline


def run_realtime():

    print("=== REAL-TIME CONNECTOR STARTED ===")

    # 1. Maahi's collector fetches fresh news
    print("Fetching fresh news...")
    collect_all_queries()

    # 2. Your ETL pipeline processes the new data
    print("Running ETL pipeline...")
    events = run_pipeline(use_geocoding=True)

    print(f"=== REAL-TIME CONNECTOR FINISHED — {len(events)} events ===")


if __name__ == "__main__":
    run_realtime()