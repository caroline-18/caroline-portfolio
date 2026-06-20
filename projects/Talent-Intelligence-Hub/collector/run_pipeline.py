import subprocess

scripts = [
    "collector/api_client.py",
    "collector/cleaner.py",
    "collector/skill_extractor.py",
    "collector/skill_summary.py",
    "collector/city_summary.py",
    "collector/company_summary.py"
]

for script in scripts:
    print(f"\nRunning {script} ...")
    subprocess.run(["python", script])

print("\nPipeline completed successfully!")