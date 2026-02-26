from job_profile.resume_profiler import infer_job_from_resume
from resume_parser.parser import parse_resume
from pathlib import Path

# Change this to your actual resume path
RESUME_PATH = Path("102.pdf")


def main():
    print("\n--- DEBUG INFERENCE TEST ---\n")

    resume = parse_resume(RESUME_PATH)

    print("Extracted skills:", resume.get("skills"))
    print("Experience:", resume.get("experience_years"))
    print("Education level:", resume.get("education_level"))

    result = infer_job_from_resume(resume)

    print("\n--- FINAL INFERENCE RESULT ---")
    for k, v in result.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
