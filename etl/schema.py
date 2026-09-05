"""
schema.py
FINAL common structure — har processed event isi shape mein hoga,
chahe wo weather se aaya ho, news se, government se, disaster se, ya transport se.

Ye schema SABHI sources ke liye ek jaisa hai. Agar koi field kisi
particular source se nahi milti, wo None/Unknown rahegi — usse
ban-ban ke value mat dalna (data quality ke liye important).
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class DisruptionEvent:

    # ================================================================
    # 1. BASIC EVENT INFORMATION
    # ================================================================
    event_id: str                              # e.g. "E0001" — hum generate karenge
    event_date: Optional[str] = None           # "2025-07-15"
    event_time: Optional[str] = None           # "14:30"
    event_type: Optional[str] = None           # Accident, Landslide, Flood, etc.
    event_description: Optional[str] = None    # "Multi-vehicle collision"

    # ================================================================
    # 2. HIGHWAY INFORMATION
    # ================================================================
    highway_id: Optional[str] = None           # "HW044"
    highway_name: Optional[str] = None         # "NH-44"
    highway_number: Optional[str] = None       # "44"
    road_type: Optional[str] = None            # "National Highway"
    state: Optional[str] = None                # "Jammu & Kashmir"
    district: Optional[str] = None             # "Ramban"

    # ================================================================
    # 3. LOCATION INFORMATION
    # ================================================================
    location: Optional[str] = None             # "Ramban"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    landmark: Optional[str] = None              # "Near Banihal Tunnel"

    # ================================================================
    # 4. CAUSE / TRIGGER
    # ================================================================
    cause: Optional[str] = None                 # "Heavy rainfall"
    trigger: Optional[str] = None                # "Landslide"
    weather_related: Optional[str] = None        # "Yes" / "No"
    environmental_factor: Optional[str] = None   # "Rainfall"

    # ================================================================
    # 5. SEVERITY
    # ================================================================
    severity: Optional[str] = None               # "Low" / "Medium" / "High" / "Critical"
    severity_score: Optional[int] = None          # 1 / 2 / 3 / 4
    road_status: Optional[str] = None             # "Blocked"

    # ================================================================
    # 6. IMPACT INFORMATION
    # ================================================================
    traffic_impact: Optional[str] = None          # "Severe"
    delay_minutes: Optional[int] = None
    road_blocked: Optional[str] = None             # "Yes" / "No"
    diversion_required: Optional[str] = None       # "Yes" / "No"
    vehicles_affected: Optional[int] = None

    # ================================================================
    # 7. CASUALTIES / DAMAGE
    # ================================================================
    fatalities: Optional[int] = None
    injuries: Optional[int] = None
    vehicles_involved: Optional[int] = None
    property_damage: Optional[str] = None          # "Yes" / "No"
    road_damage: Optional[str] = None              # "Yes" / "No"

    # ================================================================
    # 8. WEATHER INFORMATION
    # ================================================================
    weather_condition: Optional[str] = None        # "Heavy Rain"
    temperature: Optional[str] = None               # "18°C"
    rainfall_mm: Optional[float] = None
    visibility_km: Optional[float] = None
    wind_speed: Optional[str] = None                 # "25 km/h"
    snowfall: Optional[str] = None                   # "Yes" / "No"

    # ================================================================
    # 9. SOURCE INFORMATION  (extremely important)
    # ================================================================
    source_id: Optional[str] = None                 # "SRC001"
    source_name: Optional[str] = None                # "Government Advisory"
    source_type: Optional[str] = None                # "Government" / "News" / "Weather" / "Disaster" / "Transport"
    source_url: Optional[str] = None
    published_date: Optional[str] = None
    collected_date: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    def to_dict(self) -> dict:
        return asdict(self)


# Ye fields kabhi khaali nahi honi chahiye — baaki sab optional hain
REQUIRED_FIELDS = ["event_id", "source_id", "source_type"]

# Schema ke sab field names ki list — extract.py, clean.py, pipeline.py isse use karenge
# taaki har jagah field names hardcode na karne pade
SCHEMA_FIELDS = list(DisruptionEvent.__dataclass_fields__.keys())


if __name__ == "__main__":
    sample = DisruptionEvent(
        event_id="E0001",
        event_date="2025-07-15",
        event_type="Accident",
        event_description="Multi-vehicle collision",
        highway_name="NH-44",
        state="Jammu & Kashmir",
        district="Ramban",
        location="Ramban",
        latitude=33.24,
        longitude=75.24,
        cause="Heavy rainfall",
        weather_related="Yes",
        severity="High",
        severity_score=3,
        road_status="Blocked",
        source_id="SRC001",
        source_name="Government Advisory",
        source_type="Government",
        published_date="2025-07-15",
    )

    print("Sample event:")
    print(sample)
    print("\nTotal schema fields:", len(SCHEMA_FIELDS))
    print("\nAs dictionary:")
    print(sample.to_dict())