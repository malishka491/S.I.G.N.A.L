import sqlite3

db_file = "data/processed/india_highway.db"

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

cursor.execute("""
CREATE VIEW IF NOT EXISTS state_crash_summary AS
SELECT
    State,
    COUNT(*) AS Total_Crashes,
    SUM(Killed) AS Total_Killed,
    SUM(Injured) AS Total_Injured
FROM highway_crashes
GROUP BY State
ORDER BY Total_Crashes DESC;
""")
conn.commit()
print("Curated view created: state_crash_summary")




# Check the curated view
print("\nSTATE CRASH SUMMARY")
cursor.execute("SELECT * FROM state_crash_summary")
results = cursor.fetchall()
for row in results:
    print(row)



# Create NH vs SH summary view
cursor.execute("""
CREATE VIEW IF NOT EXISTS road_type_summary AS
SELECT
    "Road Type",
    COUNT(*) AS Total_Crashes,
    SUM(Killed) AS Total_Killed,
    SUM(Injured) AS Total_Injured
FROM highway_crashes
GROUP BY "Road Type";
""")



print("\nCurated view created: road_type_summary")
print("\nROAD TYPE SUMMARY")
cursor.execute("SELECT * FROM road_type_summary")
results = cursor.fetchall()
for row in results:
    print(row)



    # Create yearly summary view
cursor.execute("""
CREATE VIEW IF NOT EXISTS year_crash_summary AS
SELECT
    Crash_Year,
    COUNT(*) AS Total_Crashes,
    SUM(Killed) AS Total_Killed,
    SUM(Injured) AS Total_Injured
FROM highway_crashes
GROUP BY Crash_Year
ORDER BY Crash_Year;
""")

conn.commit()

print("\nCurated view created: year_crash_summary")

# Check the view
print("\n===== YEAR CRASH SUMMARY =====")

cursor.execute("SELECT * FROM year_crash_summary")

results = cursor.fetchall()

for row in results:
    print(row)
    conn.close()