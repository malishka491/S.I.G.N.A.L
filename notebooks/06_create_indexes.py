import sqlite3

db_file = "data/processed/india_highway.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_state
ON highway_crashes("State")
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_road_type
ON highway_crashes("Road Type")
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_crash_date
ON highway_crashes("Crash Date")
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_crash_year
ON highway_crashes("Crash_Year")
""")
conn.commit()
print("Indexes created successfully.")
conn.close()