import json
from pathlib import Path

# Input and output files
input_file = Path("data/processed/disruption_events.json")
valid_file = Path("data/processed/valid_events.json")
invalid_file = Path("data/processed/invalid_events.json")

# Read the original JSON
with open(input_file, "r", encoding="utf-8") as file:
    events = json.load(file)

valid_events = []
invalid_events = []

# Fields required by the current PostgreSQL table
required_fields = [
    "event_id",
    "event_type",
    "source_id",
    "source_type"
]

for event in events:
    missing_fields = []

    for field in required_fields:
        value = event.get(field)

        if value is None or value == "":
            missing_fields.append(field)

    if missing_fields:
        invalid_events.append({
            "record": event,
            "missing_fields": missing_fields
        })
    else:
        valid_events.append(event)

# Save valid records
with open(valid_file, "w", encoding="utf-8") as file:
    json.dump(valid_events, file, indent=2, ensure_ascii=False)

# Save invalid records separately
with open(invalid_file, "w", encoding="utf-8") as file:
    json.dump(invalid_events, file, indent=2, ensure_ascii=False)

print(f"Total records: {len(events)}")
print(f"Valid records: {len(valid_events)}")
print(f"Invalid records: {len(invalid_events)}")
print(f"Valid file: {valid_file}")
print(f"Invalid file: {invalid_file}")