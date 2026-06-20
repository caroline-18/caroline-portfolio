import pandas as pd

INPUT_FILE = "data/processed/jobs_clean.csv"
OUTPUT_FILE = "data/processed/city_summary.csv"

df = pd.read_csv(INPUT_FILE)

summary = (
    df["city"]
    .fillna("Remote / Not Specified")
    .replace("", "Remote / Not Specified")
    .value_counts()
    .reset_index()
)

summary.columns = ["city", "count"]

summary.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("✅ City summary created!")
print(summary)