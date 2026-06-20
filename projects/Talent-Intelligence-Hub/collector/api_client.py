import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

print("APP_ID:", APP_ID)
print("APP_KEY:", APP_KEY)

SEARCH_TERMS = [

    "Data Scientist",

    "Machine Learning Engineer",

    "Data Analyst",

    "Data Engineer",

    "AI Engineer",

    "GenAI Engineer",

    "LLM Engineer",

    "NLP Engineer",

    "MLOps Engineer",

    "Business Analyst"

]

all_jobs = []

for search_term in SEARCH_TERMS:

    print()
    print(f"===== {search_term} =====")

    for page in range(1, 6):

        url = (
            f"https://api.adzuna.com/v1/api/jobs/in/search/{page}"
            f"?app_id={APP_ID}"
            f"&app_key={APP_KEY}"
            f"&results_per_page=50"
            f"&what={search_term.replace(' ', '%20')}"
            f"&content-type=application/json"
        )

        print(f"Downloading page {page}...")

        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()

            jobs = data.get("results", [])

            print(f"Found {len(jobs)} jobs.")

            for job in jobs:

                job["search_term"] = search_term

                all_jobs.append(job)

        else:

            print(f"Error for {search_term}")
            print(response.status_code)

# Remove duplicate jobs

unique_jobs = {}

for job in all_jobs:

    unique_jobs[job["id"]] = job

final_data = {
    "results": list(unique_jobs.values())
}

with open(
    "data/raw/jobs_raw.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        final_data,
        file,
        indent=4
    )

print()
print("✅ Download Complete!")
print(f"Total Unique Jobs Collected: {len(final_data['results'])}")