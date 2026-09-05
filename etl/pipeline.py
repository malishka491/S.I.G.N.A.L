"""
pipeline.py
MAIN ENTRY POINT — poori ETL pipeline ko sahi order mein chalata hai:
Extract -> Clean -> NLP Enrich -> Geocode -> Deduplicate -> Save
"""

import csv
import json
import os
from etl.load_json_to_postgres import load_json_to_postgres
from etl.utils.logger_config import get_logger
from etl.extract import extract_all_sources
from etl.clean import clean_records
from etl.nlp_processor import enrich_records
from etl.geocode import geocode_records
from etl.deduplicate import deduplicate_records
from etl.schema import DisruptionEvent, SCHEMA_FIELDS

logger = get_logger(__name__)


def assign_event_ids(records: list) -> list:
    for i, record in enumerate(records, start=1):
        record["event_id"] = f"E{i:05d}"
    return records


def build_final_events(records: list) -> list:
    events = []
    for record in records:
        filtered = {k: v for k, v in record.items() if k in SCHEMA_FIELDS}
        events.append(DisruptionEvent(**filtered))
    return events


def save_to_csv(events: list, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SCHEMA_FIELDS)
        writer.writeheader()
        for event in events:
            writer.writerow(event.to_dict())
    logger.info(f"Saved {len(events)} events to {output_path}")


def save_to_json(events: list, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([e.to_dict() for e in events], f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(events)} events to {output_path}")


def run_pipeline(
    use_geocoding: bool = True,
    selected_files: list = None
):
    logger.info("=== ETL PIPELINE STARTED ===")

    raw = extract_all_sources(selected_files=selected_files)
    if not raw:
        logger.warning("Koi raw data nahi mila. Pipeline rok rahe hain.")
        return []

    cleaned = clean_records(raw)
    enriched = enrich_records(cleaned)

    if use_geocoding:
        enriched = geocode_records(enriched)

    deduped = deduplicate_records(enriched)
    deduped = assign_event_ids(deduped)
    events = build_final_events(deduped)

    save_to_csv(events, os.path.join("data", "cleaned", "disruption_events.csv"))
    save_to_json(events, os.path.join("data", "processed", "disruption_events.json"))
    load_json_to_postgres()
    logger.info(f"=== ETL PIPELINE FINISHED — {len(events)} final events ===")
    return events


if __name__ == "__main__":
    final_events = run_pipeline(use_geocoding=True)
    print(f"\nPipeline complete. Total final events: {len(final_events)}")
    if final_events:
        print("\nSample final event:")
        print(final_events[0])