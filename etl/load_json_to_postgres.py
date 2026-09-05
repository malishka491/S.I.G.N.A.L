import json
import psycopg
from pathlib import Path

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "highway_db",
    "user": "highway_user",
    "password": "highway_password_2026"
}

JSON_PATH = Path("data/processed/disruption_events.json")


def main():
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

            for event in events:
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
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
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
                        raw_data = EXCLUDED.raw_data;
                """, (
                    event.get("event_id"),
                    event.get("event_date"),
                    event.get("event_type"),
                    event.get("location"),
                    event.get("latitude"),
                    event.get("longitude"),
                    event.get("source_id"),
                    event.get("source_name"),
                    event.get("source_type"),
                    json.dumps(event)
                ))

        conn.commit()

    print(f"Records processed successfully: {len(events)}")
    print("Database connection closed")


if __name__ == "__main__":
    main()