import pandas as pd

INPUT_FILE = "data/processed/job_skills.csv"
OUTPUT_FILE = "data/processed/skill_summary.csv"

df = pd.read_csv(INPUT_FILE)

summary = (
    df["skill"]
    .value_counts()
    .reset_index()
)

summary.columns = ["skill", "count"]

summary.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("✅ Skill summary created!")
print(summary)