from pathlib import Path

# Resume parsing
from resume_parser.parser import parse_resume

# Job parsing
from job_profile.job_parser import load_all_jobs

# Multi-job matching
from matching.multi_job_matcher import match_resume_to_jobs

# ATS feedback & improvement
from analysis.rejection_feedback import generate_rejection_feedback

# Export
from utils.export_utils import export_to_csv


def main():
    # -----------------------------
    # CONFIG
    # -----------------------------
    RESUME_DIR = Path("Resume_data")
    JOB_DIR = Path("job_profile/jobs")
    OUTPUT_FILE = Path("output/resume_ranking.csv")
    SHORTLIST_THRESHOLD = 60.0

    # -----------------------------
    # LOAD JOBS
    # -----------------------------
    jobs = load_all_jobs(JOB_DIR)

    if not jobs:
        print("❌ No job descriptions found in job_profile/jobs/")
        return

    print("\n========== JOB PROFILES LOADED ==========")
    for job_name in jobs:
        print(f"• {job_name}")
    print("========================================\n")

    # -----------------------------
    # LOAD RESUMES
    # -----------------------------
    resume_files = sorted(RESUME_DIR.glob("*.pdf"))

    if not resume_files:
        print("❌ No resumes found in Resume_data/")
        return

    results = []

    # -----------------------------
    # PROCESS EACH RESUME
    # -----------------------------
    for resume_path in resume_files:
        print(f"\n📄 Processing {resume_path.name} ...")

        resume = parse_resume(resume_path)

        job_matches = match_resume_to_jobs(resume, jobs)
        best_job = job_matches[0]

        feedback = generate_rejection_feedback(
            resume_name=resume_path.name,
            score=best_job["score"],
            matched_skills=best_job["matched_skills"],
            missing_skills=best_job["missing_skills"],
            threshold=SHORTLIST_THRESHOLD
        )

        results.append({
            "file": resume_path.name,
            "best_job": best_job["job"],
            "score": best_job["score"],
            "improvement_score": best_job["improvement_score"],
            "matched_skills": best_job["matched_skills"],
            "missing_skills": best_job["missing_skills"],
            "feedback": feedback
        })

    # -----------------------------
    # SORT BY BEST JOB SCORE
    # -----------------------------
    results.sort(key=lambda x: x["score"], reverse=True)

    # -----------------------------
    # DISPLAY RANKING
    # -----------------------------
    print("\n========== RESUME → BEST JOB MATCH ==========\n")

    for idx, r in enumerate(results, 1):
        print(f"{idx:02d}. {r['file']}")
        print(f"    🎯 Best Fit Job : {r['best_job']}")
        print(f"    📊 Score       : {r['score']:.1f}%")
        print(f"    🚀 Potential   : {r['improvement_score']:.1f}%")
        print(f"    ✓ Matched      : {', '.join(r['matched_skills']) or 'None'}")
        print(f"    ✗ Missing      : {', '.join(r['missing_skills']) or 'None'}\n")

    print("============================================\n")

    # -----------------------------
    # SHORTLIST
    # -----------------------------
    shortlisted = [r for r in results if r["score"] >= SHORTLIST_THRESHOLD]

    print(f"✅ Shortlisted {len(shortlisted)} / {len(results)} resumes (≥ {SHORTLIST_THRESHOLD}%)\n")

    for r in shortlisted:
        print(f"✔ {r['file']} → {r['best_job']} ({r['score']:.1f}%)")

    # -----------------------------
    # ATS FEEDBACK
    # -----------------------------
    print("\n========== ATS FEEDBACK ==========\n")

    for r in results:
        fb = r["feedback"]
        print(f"📄 {fb['resume']} — {fb['status']} ({fb['score']}%)")

        if fb["suggestions"]:
            for s in fb["suggestions"]:
                print(f"  • {s}")
        else:
            print("  ✓ Resume is ATS optimized")

        print()

    # -----------------------------
    # EXPORT TO CSV
    # -----------------------------
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    export_to_csv(results, OUTPUT_FILE)

    print("📁 CSV exported to output/resume_ranking.csv")
    print("\n🎯 Multi-Job Resume Matching Complete")


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()
