import pandas as pd

file_path = "data/raw/news/Media Reported Road Traffic Crash Data/Data Files/News Crashes.xlsx"

df = pd.read_excel(file_path)
print("Original records:", len(df))
print("Original columns:", len(df.columns))
df.columns = df.columns.str.strip()
print("\nCleaned column names:")
print(df.columns.tolist())


text_columns = [
    "Month", "Crash Day", "Location", "Million Plus City",
    "State", "Vehicle 1", "Vehicle/Object 2",
    "Gender", "Road Type", "Crash Type"
]
for col in text_columns:
    df[col] = df[col].astype("string").str.strip()
print("\nText fields cleaned successfully.")


state_corrections = {
    "Chhatisgarh": "Chhattisgarh"
}
df["State"] = df["State"].replace(state_corrections)
print("\nState names after standardization:")
print(df["State"].value_counts())


df["Road Type"] = df["Road Type"].str.upper().str.strip()
print("\nRoad Type after standardization:")
print(df["Road Type"].value_counts())


df["Crash Date"] = pd.to_datetime(
    df["Crash Date"],
    errors="coerce"
)
df["Article Date"] = pd.to_datetime(
    df["Article Date"],
    errors="coerce"
)
print("\nDate columns cleaned:")
print("Missing Crash Dates:", df["Crash Date"].isna().sum())
print("Missing Article Dates:", df["Article Date"].isna().sum())


df[["Latitude", "Longitude"]] = df["LatLong"].str.split(
    ",", expand=True
)
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
print("\nCoordinates cleaned:")
print("Missing Latitude:", df["Latitude"].isna().sum())
print("Missing Longitude:", df["Longitude"].isna().sum())


print("\nOriginal Age values:")
print(df["Age"].value_counts(dropna=False).head(30))
# df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
print("\nAge column:")
print("Missing Age:", df["Age"].isna().sum())
print("Age data type:", df["Age"].dtype)
print("\nNon-numeric Age values:")
print(
    df.loc[
        pd.to_numeric(df["Age"], errors="coerce").isna()
        & df["Age"].notna(),
        "Age"
    ].value_counts()
)
age_split = (
    df["Age"]
    .dropna()
    .astype(str)
    .str.split(",")
)

def clean_ages(age_list):
    ages = []

    for age in age_list:
        try:
            value = float(age.strip())

            if 0 < value <= 120:
                ages.append(value)

        except ValueError:
            continue

    return ages

cleaned_ages = age_split.apply(clean_ages)
df["Age_Count"] = cleaned_ages.apply(len)
df["Average_Age"] = cleaned_ages.apply(
    lambda x: sum(x) / len(x) if len(x) > 0 else None
)
df["Minimum_Age"] = cleaned_ages.apply(
    lambda x: min(x) if len(x) > 0 else None
)
df["Maximum_Age"] = cleaned_ages.apply(
    lambda x: max(x) if len(x) > 0 else None
)
print("\nAge features created:")
print(
    df[
        ["Age", "Age_Count", "Average_Age",
         "Minimum_Age", "Maximum_Age"]
    ].head(10)
)


print("\nKilled and Injured validation:")
print("Negative Killed:", (df["Killed"] < 0).sum())
print("Negative Injured:", (df["Injured"] < 0).sum())
print("Missing Killed:", df["Killed"].isna().sum())
print("Missing Injured:", df["Injured"].isna().sum())


df["Gender"] = df["Gender"].str.strip().str.upper()
print("\nGender values:")
print(df["Gender"].value_counts(dropna=False))


print("\nCrash Type values:")
print(df["Crash Type"].value_counts(dropna=False))
df["Crash Type"] = df["Crash Type"].replace(
    {"WIth Parked Vehicle": "With Parked Vehicle"}
)
print("\nCrash Type after standardization:")
print(df["Crash Type"].value_counts(dropna=False))


vehicle_columns = ["Vehicle 1", "Vehicle/Object 2"]
for col in vehicle_columns:
    df[col] = df[col].str.strip().str.upper()
print("\nVehicle columns cleaned:")
print("\nVehicle 1:")
print(df["Vehicle 1"].value_counts(dropna=False).head(20))
print("\nVehicle/Object 2:")
print(df["Vehicle/Object 2"].value_counts(dropna=False).head(20))
object_categories = {
    "DIVIDER", "TREE", "DITCH", "POLE", "WALL",
    "CANAL", "RIVER", "GORGE"
}
df["Object_2_Type"] = df["Vehicle/Object 2"].apply(
    lambda x: (
        "OBJECT" if x in object_categories
        else "UNKNOWN" if x in ["NIL", "UNIDENTIFIED"]
        else "VEHICLE"
    )
)
print("\nVehicle/Object 2 classification:")
print(df["Object_2_Type"].value_counts(dropna=False))


print("\nMonth values:")
print(df["Month"].value_counts())
print("\nCrash Day values:")
print(df["Crash Day"].value_counts())
df["Crash_Year"] = df["Crash Date"].dt.year
df["Crash_Month_Number"] = df["Crash Date"].dt.month
df["Crash_Day_Number"] = df["Crash Date"].dt.dayofweek
print("\nTime features created:")
print(
    df[
        ["Crash Date", "Crash_Year",
         "Crash_Month_Number", "Crash_Day_Number"]
    ].head()
)

#highway identification
highway_df = df[df["Road Type"].isin(["NH", "SH"])].copy()

print("\nHighway-focused dataset:")
print("Total highway records:", len(highway_df))
print("NH records:", (highway_df["Road Type"] == "NH").sum())
print("SH records:", (highway_df["Road Type"] == "SH").sum())
highway_df["Highway_Number"] = pd.NA
print("\nHighway number column created.")
print(highway_df[[
    "Location",
    "State",
    "Road Type",
    "Latitude",
    "Longitude",
    "Highway_Number"
]].head())

print("\n===== ROAD TYPE COUNTS =====")
print(df["Road Type"].value_counts(dropna=False))

print("\n===== STATES =====")
print(df["State"].nunique())
print(df["State"].unique())


# ===== SPLIT LATITUDE AND LONGITUDE =====

df[["Latitude", "Longitude"]] = (
    df["LatLong"]
    .str.split(",", expand=True)
)


df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
print("\n===== COORDINATES =====")
print(df[["LatLong", "Latitude", "Longitude"]].head())
print("\nMissing Latitude:", df["Latitude"].isna().sum())
print("Missing Longitude:", df["Longitude"].isna().sum())


# Check if coordinates are valid
print("\nCHECKING COORDINATES")
print("Latitude:")
print(df["Latitude"].min(), "to", df["Latitude"].max())
print("Longitude:")
print(df["Longitude"].min(), "to", df["Longitude"].max())
print("Missing Latitude:", df["Latitude"].isna().sum())
print("Missing Longitude:", df["Longitude"].isna().sum())


# Count NH and SH records
print("\nNH AND SH RECORDS")
nh = (df["Road Type"] == "NH").sum()
sh = (df["Road Type"] == "SH").sum()
print("National Highway records:", nh)
print("State Highway records:", sh)
print("Total NH + SH:", nh + sh)


# Keep only National and State Highway records
highway_df = df[df["Road Type"].isin(["NH", "SH"])].copy()
print("\n===== HIGHWAY DATASET =====")
print("Total records:", len(highway_df))
print("NH records:", (highway_df["Road Type"] == "NH").sum())
print("SH records:", (highway_df["Road Type"] == "SH").sum())


# Check NH and SH records by state
print("\nHIGHWAY RECORDS BY STATE")
print(highway_df["State"].value_counts())


print("\nFINAL QUALITY CHECK")

print("Total records:", len(highway_df))
print("Duplicate records:", highway_df.duplicated().sum())
print("\nMissing values:")
print(highway_df.isnull().sum())
print("\nData types:")
print(highway_df.dtypes)
print("\nInvalid Killed values:", (highway_df["Killed"] < 0).sum())
print("Invalid Injured values:", (highway_df["Injured"] < 0).sum())

from pathlib import Path

output_folder = Path("data/processed")
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "historical_highway_crashes.csv"

highway_df.to_csv(output_file, index=False)

print("\nFinal dataset saved to:", output_file)
print("Records saved:", len(highway_df))