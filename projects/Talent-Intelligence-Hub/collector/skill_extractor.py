import pandas as pd
import re

INPUT_FILE = "data/processed/jobs_clean.csv"
OUTPUT_FILE = "data/processed/job_skills.csv"

SKILLS = [
    "Python",
    "SQL",
    "Excel",
    "Power BI",
    "Tableau",
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "LLM",
    "GenAI",
    "AWS",
    "Azure",
    "GCP",
    "Databricks",
    "PySpark",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
    "LangChain",
    "OpenAI",
    "Statistics",
    "R",
    "JavaScript",
    "Kubernetes",
    "Docker",
    "BigQuery",
    "Vertex AI",
    "MLOps"
]

df = pd.read_csv(INPUT_FILE)
extracted_skills = []

for _, row in df.iterrows():

    description = str(row["description"]).lower()

    for skill in SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, description):
            extracted_skills.append({
                "job_id": row["job_id"],
                "title": row["title"],
                "company": row["company"],
                "skill": skill
            })

skills_df = pd.DataFrame(extracted_skills)

skills_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("✅ Skills extracted successfully!")
print(f"Total skills found: {len(skills_df)}")
print(f"Saved to: {OUTPUT_FILE}")