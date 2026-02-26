from job_loader import load_all_jobs

jobs = load_all_jobs()
print(f"Loaded {len(jobs)} jobs")

for k, v in list(jobs.items())[:3]:
    print(k, "->", v["title"], "|", v["domain"])
