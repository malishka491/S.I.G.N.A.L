import json
import hashlib
import psycopg
from pathlib import Path


def clean_date(value):
    """
    Convert empty date strings into None.
    PostgreSQL stores None as NULL.
    """
    if value is None or str(value).strip() == "":
        return None

    return value


def make_stable_event_id(event):
    """
    Generate a stable ID from the article URL.

    The same article gets the same ID across different runs.
    A new article gets a different ID.
    """
    source_url = str(event.get("source_url") or "").strip()

    if source_url:
        return "URL_" + hashlib.sha256(
            source_url.encode("utf-8")
        ).hexdigest()

    # Fallback if the article has no URL
    raw_text = str(event.get("raw_text") or "").strip()

    return "TEXT_" + hashlib.sha256(
        raw_text.encode("utf-8")
    ).hexdigest()


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "highway_db",
    "user": "highway_user",
    "password": "highway_password_2026"
}

JSON_PATH = Path("data/processed/disruption_events.json")


def load_json_to_postgres():

    with open(JSON_PATH, "r", encoding="utf-8") as file:
        events = json.load(file)

    print(f"JSON records loaded: {len(events)}")

    with psycopg.connect(**DB_CONFIG) as conn:

        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS realtime_events (
                    id SERIAL PRIMARY KEY,
                    json_event_id TEXT UNIQUE,
                    event_date DATE,
                    event_type TEXT,
                    location TEXT,
                    latitude NUMERIC,
                    longitude NUMERIC,
                    source_id TEXT,
                    source_name TEXT,
                    source_type TEXT,
                    raw_data JSONB NOT NULL,
                    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            inserted_count = 0
            updated_count = 0

            for event in events:

                stable_id = make_stable_event_id(event)

                cur.execute("""
                    INSERT INTO realtime_events (
                        json_event_id,
                        event_date,
                        event_type,
                        location,
                        latitude,
                        longitude,
                        source_id,
                        source_name,
                        source_type,
                        raw_data
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)

                    ON CONFLICT (json_event_id)
                    DO UPDATE SET
                        event_date = EXCLUDED.event_date,
                        event_type = EXCLUDED.event_type,
                        location = EXCLUDED.location,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        source_id = EXCLUDED.source_id,
                        source_name = EXCLUDED.source_name,
                        source_type = EXCLUDED.source_type,
                        raw_data = EXCLUDED.raw_data

                    RETURNING (xmax = 0) AS inserted;
                """, (
                    stable_id,
                    clean_date(event.get("event_date")),
                    event.get("event_type"),
                    event.get("location"),
                    event.get("latitude"),
                    event.get("longitude"),
                    event.get("source_id"),
                    event.get("source_name"),
                    event.get("source_type"),
                    json.dumps(event)
                ))

                was_inserted = cur.fetchone()[0]

                if was_inserted:
                    inserted_count += 1
                else:
                    updated_count += 1

        conn.commit()

    print(f"New records inserted: {inserted_count}")
    print(f"Existing records updated: {updated_count}")
    print(f"Total records processed: {len(events)}")
    print("Database connection closed")


if __name__ == "__main__":
    load_json_to_postgres()