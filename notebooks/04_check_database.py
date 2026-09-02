import sqlite3

db_file = "data/processed/india_highway.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM highway_crashes")
count = cursor.fetchone()[0]
print("Records in database:", count)
cursor.execute("SELECT * FROM highway_crashes LIMIT 5")
rows = cursor.fetchall()
print("\nFirst 5 records:")
for row in rows:
    print(row)
conn.close()