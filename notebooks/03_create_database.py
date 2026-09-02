from pathlib import Path
import sqlite3
import pandas as pd

csv_file = Path("data/processed/historical_highway_crashes.csv")
db_file = Path("data/processed/india_highway.db")
df = pd.read_csv(csv_file)
conn = sqlite3.connect(db_file)
df.to_sql("highway_crashes", conn, if_exists="replace", index=False)
print("Database created:", db_file)
print("Table created: highway_crashes")
print("Records stored:", len(df))
conn.close()