from dotenv import load_dotenv
import os

load_dotenv()

app_id = os.getenv("ADZUNA_APP_ID")
app_key = os.getenv("ADZUNA_APP_KEY")

print("Environment loaded successfully!")

if app_id and app_key:
    print("✅ API credentials found.")
else:
    print("❌ API credentials missing.")