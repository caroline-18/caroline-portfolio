import pandas as pd

INPUT_FILE = "data/processed/jobs_clean.csv"
OUTPUT_FILE = "data/processed/company_summary.csv"

df = pd.read_csv(INPUT_FILE)

summary = (
    df["company"]
    .fillna("Unknown")
    .value_counts()
    .reset_index()
)

summary.columns = ["company", "count"]

summary.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("✅ Company summary created!")
print(summary)