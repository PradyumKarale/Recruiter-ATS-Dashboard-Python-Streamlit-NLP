import csv
from analysis.education_levels import EDU_LEVELS

# reverse map: 2 -> Bachelor
EDU_LABELS = {v: k.capitalize() for k, v in EDU_LEVELS.items()}


def export_to_csv(results, output_path, shortlist_threshold):
    """
    Recruiter-ready ATS CSV (explanatory, decision-friendly)
    """

    headers = [
        "Rank",
        "Candidate Name",
        "Resume File",
        "Email",
        "Phone",

        "Final Verdict",
        "Confidence Band",
        "Overall Score (%)",
        "Potential Score (%)",

        "Best Fit Job",
        "Domain",
        "Seniority",

        "JD Min Education",
        "Candidate Education",
        "Education Match",

        "Experience (Years)",

        "Why Candidate Fits",
        "Why Candidate Rejected",
        "Compared Against",

        "Matched Skills",
        "Missing Skills"
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for idx, r in enumerate(results, start=1):
            resume = r.get("resume", {})

            # --- education labels ---
            jd_edu = r.get("jd_min_education", -1)
            resume_edu = resume.get("education_level", -1)

            jd_edu_label = EDU_LABELS.get(jd_edu, "Not specified")
            resume_edu_label = EDU_LABELS.get(resume_edu, "Not found")

            # --- final verdict ---
            if r.get("rejection_reasons"):
                verdict = "Rejected"
            elif r.get("confidence_band") in ["Strong Fit", "Good Fit"]:
                verdict = "Proceed to Interview"
            elif r.get("confidence_band") == "Borderline":
                verdict = "Review Manually"
            else:
                verdict = "Low Priority"

            # --- safe string extraction ---
            def safe_join(val):
                if isinstance(val, list):
                    return ", ".join(val)
                if isinstance(val, str):
                    return val
                return "Not found"

            writer.writerow({
                "Rank": idx,

                "Candidate Name": safe_join(resume.get("name")),
                "Resume File": r.get("filename", "Unknown"),
                "Email": safe_join(resume.get("email")),
                "Phone": safe_join(resume.get("phone")),

                "Final Verdict": verdict,
                "Confidence Band": r.get("confidence_band", "Unknown"),
                "Overall Score (%)": r.get("score", 0),
                "Potential Score (%)": r.get("improvement_score", 0),

                "Best Fit Job": r.get("best_fit_job", "Unknown"),
                "Domain": r.get("domain", "Unknown"),
                "Seniority": r.get("seniority", "Unknown"),

                "JD Min Education": jd_edu_label,
                "Candidate Education": resume_edu_label,
                "Education Match": r.get("education_match", "not_required"),

                "Experience (Years)": resume.get("experience_years", "Not found"),

                "Why Candidate Fits": " | ".join(r.get("fit_reasons", [])),
                "Why Candidate Rejected": " | ".join(r.get("rejection_reasons", [])),

                "Compared Against": " | ".join(
                    f"{c.get('job_title', '')} ({c.get('confidence', 0)}%)"
                    for c in r.get("compared_against", [])
                ),

                "Matched Skills": ", ".join(r.get("matched_skills", [])),
                "Missing Skills": ", ".join(r.get("missing_skills", [])),
            })
