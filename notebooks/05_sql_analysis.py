import sqlite3

db_file = "data/processed/india_highway.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

query = """
SELECT State, COUNT(*) AS Total_Crashes
FROM highway_crashes
GROUP BY State
ORDER BY Total_Crashes DESC;
"""
cursor.execute(query)
results = cursor.fetchall()
print("CRASHES BY STATE")
for state, crashes in results:
    print(state, ":", crashes)



print("\nFATALITIES BY STATE")
query = """
SELECT State, SUM(Killed) AS Total_Killed
FROM highway_crashes
GROUP BY State
ORDER BY Total_Killed DESC;
"""
cursor.execute(query)
results = cursor.fetchall()
for state, killed in results:
    print(state, ":", killed)




# Query 3: Injuries by state
print("\nINJURIES BY STATE")
query = """
SELECT State, SUM(Injured) AS Total_Injured
FROM highway_crashes
GROUP BY State
ORDER BY Total_Injured DESC;
"""
cursor.execute(query)
results = cursor.fetchall()
for state, injured in results:
    print(state, ":", injured)




# Query 4: NH vs SH
print("\n===== NH VS SH CRASHES =====")
query = """
SELECT "Road Type", COUNT(*) AS Total_Crashes,
       SUM(Killed) AS Total_Killed,
       SUM(Injured) AS Total_Injured
FROM highway_crashes
GROUP BY "Road Type"
ORDER BY Total_Crashes DESC;
"""
cursor.execute(query)
results = cursor.fetchall()
for road_type, crashes, killed, injured in results:
    print(road_type, "| Crashes:", crashes,
          "| Killed:", killed,
          "| Injured:", injured)




    # Query 5: Crash types
print("\nCRASH TYPES")
query = """
SELECT "Crash Type", COUNT(*) AS Total_Crashes
FROM highway_crashes
GROUP BY "Crash Type"
ORDER BY Total_Crashes DESC;
"""
cursor.execute(query)
results = cursor.fetchall()
for crash_type, crashes in results:
    print(crash_type, ":", crashes)



    # Query 6: Crashes by year
print("\nCRASHES BY YEAR")
query = """
SELECT Crash_Year, COUNT(*) AS Total_Crashes
FROM highway_crashes
GROUP BY Crash_Year
ORDER BY Crash_Year;
"""
cursor.execute(query)
results = cursor.fetchall()
for year, crashes in results:
    print(year, ":", crashes)



    # Query 7: Crashes by month
print("\nCRASHES BY MONTH")
query = """
SELECT Crash_Month_Number, COUNT(*) AS Total_Crashes
FROM highway_crashes
GROUP BY Crash_Month_Number
ORDER BY Crash_Month_Number;
"""
cursor.execute(query)
results = cursor.fetchall()
for month, crashes in results:
    print("Month", month, ":", crashes)
conn.close()
