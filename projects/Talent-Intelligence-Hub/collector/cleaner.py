import json
import pandas as pd

INPUT_FILE = "data/raw/jobs_raw.json"
OUTPUT_FILE = "data/processed/jobs_clean.csv"

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

jobs = []

CITY_MAPPING = {
    "India": "Pan India",
    "Bengaluru": "Bangalore",
    "Bengaluru Urban": "Bangalore",
    "Bangalore Urban": "Bangalore",
    "Bombay": "Mumbai",
    "Madras": "Chennai",
    "Calcutta": "Kolkata",
    "Gurgaon": "Gurugram",
    "": "Unknown"
}

STATE_NAMES = {

    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Delhi",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"

}

for job in data["results"]:

    area = job.get("location", {}).get("area", [])
    display_location = job.get(
        "location",
        {}
    ).get(
        "display_name",
        ""
    )

    title = str(
        job.get(
            "title",
            ""
        )
    ).lower()

    country = (
        area[0]
        if len(area) > 0
        else "Unknown"
    )

    state = (
        area[1]
        if len(area) > 1
        else "Unknown"
    )

    work_type = "On-site"

    # City Extraction

    if len(area) >= 3:

        city = area[2]

    elif len(area) == 2:

        city = area[1]

    else:

        city = display_location

    city = str(city).strip()

    city = CITY_MAPPING.get(
        city,
        city
    )

    # Remote jobs

    if "remote" in title:

        city = "Remote"
        state = "Unknown"
        work_type = "Remote"

    # Pan India jobs

    elif city == "Pan India":

        state = "Unknown"
        work_type = "Hybrid"

    # State mistakenly detected as city

    elif city in STATE_NAMES:

        state = city
        city = "Unknown"

    # Normalize city names

    city = CITY_MAPPING.get(
        city,
        city
    )

    # Detect true remote jobs

    if "remote" in title:

        city = "Remote"

    jobs.append({

        "job_id":
            job.get("id"),

        "title":
            job.get("title"),

        "job_role":
            job.get(
                "search_term",
                "Data Scientist"
            ),

        "company":
            job.get(
                "company",
                {}
            ).get(
                "display_name"
            ),

        "category":
            job.get(
                "category",
                {}
            ).get(
                "label"
            ),

        "location":
            display_location,

        "country":
            country,

        "state":
            state,

        "city":
            city,

        "work_type":
            work_type,

        "description":
            job.get(
                "description"
            ),

        "posted_date":
            job.get(
                "created"
            ),

        "job_url":
            job.get(
                "redirect_url"
            )

    })

df = pd.DataFrame(jobs)

df["posted_date"] = pd.to_datetime(
    df["posted_date"]
)

df = df.sort_values(
    by="posted_date",
    ascending=False
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("✅ Data cleaned successfully!")
print(
    f"Total jobs processed: {len(df)}"
)
print(
    f"Saved to: {OUTPUT_FILE}"
)
