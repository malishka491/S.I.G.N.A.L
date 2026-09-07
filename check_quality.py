import json

with open("data/processed/disruption_events.json", encoding="utf-8") as f:
    data = json.load(f)

print("SOURCE TYPE BREAKDOWN:")
print("-" * 60)
source_counts = {}
for r in data:
    st = r.get("source_type", "Unknown")
    source_counts[st] = source_counts.get(st, 0) + 1
for st, count in sorted(source_counts.items(), key=lambda x: -x[1]):
    print(f"{st:15s}: {count}")

print("\nEVENT TYPE BREAKDOWN:")
print("-" * 60)
event_type_counts = {}
for r in data:
    et = r.get("event_type") or "(not detected)"
    event_type_counts[et] = event_type_counts.get(et, 0) + 1
for et, count in sorted(event_type_counts.items(), key=lambda x: -x[1]):
    print(f"{et:20s}: {count}")

print("\nSEVERITY BREAKDOWN:")
print("-" * 60)
severity_counts = {}
for r in data:
    sv = r.get("severity") or "(not detected)"
    severity_counts[sv] = severity_counts.get(sv, 0) + 1
for sv, count in sorted(severity_counts.items(), key=lambda x: -x[1]):
    print(f"{sv:20s}: {count}")

print("\nTOP 10 STATES:")
print("-" * 60)
state_counts = {}
for r in data:
    st = r.get("state")
    if st:
        state_counts[st] = state_counts.get(st, 0) + 1
for st, count in sorted(state_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"{st:20s}: {count}")

print("\nTOP HIGHWAYS:")
print("-" * 60)
highway_counts = {}
for r in data:
    hw = r.get("highway_name")
    if hw:
        highway_counts[hw] = highway_counts.get(hw, 0) + 1
for hw, count in sorted(highway_counts.items(), key=lambda x: -x[1])[:10]:
    print(f"{hw:30s}: {count}")