"""
deduplicate.py
Same event agar multiple sources se report hua hai (same date + same
location + same event_type), to unhe merge karke ek record rakhta hai.
"""

from etl.utils.logger_config import get_logger

logger = get_logger(__name__)


def make_dedup_key(record: dict) -> tuple:
    return (
        (record.get("event_date") or "").strip().lower(),
        (record.get("location") or "").strip().lower(),
        (record.get("event_type") or "").strip().lower(),
    )


def deduplicate_records(records: list) -> list:
    seen = {}
    unique_records = []

    for record in records:
        key = make_dedup_key(record)

        if key == ("", "", ""):
            unique_records.append(record)
            continue

        if key not in seen:
            seen[key] = record
            unique_records.append(record)
        else:
            existing = seen[key]
            existing_filled = sum(1 for v in existing.values() if v not in (None, ""))
            new_filled = sum(1 for v in record.values() if v not in (None, ""))
            if new_filled > existing_filled:
                idx = unique_records.index(existing)
                unique_records[idx] = record
                seen[key] = record

    removed = len(records) - len(unique_records)
    logger.info(f"Deduplication: {removed} duplicates removed, {len(unique_records)} unique records remain")
    return unique_records


if __name__ == "__main__":
    from etl.extract import extract_all_sources
    from etl.clean import clean_records
    from etl.nlp_processor import enrich_records

    raw = extract_all_sources()
    cleaned = clean_records(raw)
    enriched = enrich_records(cleaned)
    deduped = deduplicate_records(enriched)

    print(f"\nTotal unique records: {len(deduped)}")