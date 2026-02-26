from matching.jd_resume_scorer import score_resume_against_jd
from analysis.education_matcher import match_education
from job_profile.resume_profiler import infer_job_from_resume


def rank_resumes_against_jd(resumes, jd_profile, shortlist_threshold):
    """
    Ranks resumes based on:
    1) JD ↔ Resume score
    2) Resume-based job inference (domain, role, confidence)
    """

    ranked = []

    for resume_data in resumes:
        resume = resume_data["resume"]
        filename = resume_data["filename"]

        # -----------------------------
        # JD ↔ Resume scoring
        # -----------------------------
        score_data = score_resume_against_jd(resume, jd_profile)

        # -----------------------------
        # Education match (CSV only)
        # -----------------------------
        jd_edu_level = jd_profile.get("min_education_level", -1)
        resume_edu_level = resume.get("education_level", -1)

        if jd_edu_level != -1:
            education_match = match_education(jd_edu_level, resume_edu_level)
        else:
            education_match = "not_required"

        # -----------------------------
        # Shortlist status (JD score)
        # -----------------------------
        status = (
            "Shortlisted"
            if score_data["score"] >= shortlist_threshold
            else "Rejected"
        )

        # -----------------------------
        # Resume-based inference
        # -----------------------------
        resume_job = infer_job_from_resume(resume)

        ranked.append({
            # Ranking
            "rank": None,
            "filename": filename,
            "resume": resume,   # REQUIRED for CSV

            # JD score
            "score": score_data.get("score", 0.0),
            "improvement_score": score_data.get("improvement_score", 0.0),

            # Skill gaps
            "matched_skills": score_data.get("matched_skills", []),
            "missing_skills": score_data.get("missing_skills", []),

            # Status
            "status": status,

            # Resume-based inference (SAFE)
            "best_fit_job": resume_job.get("job_title", "Unknown"),
            "domain": resume_job.get("domain", "Unknown"),
            "confidence": resume_job.get("confidence", 0.0),
            "confidence_band": resume_job.get("confidence_band", "Unknown"),
            "seniority": resume_job.get("seniority", "Unknown"),

            # Explanation (USED BY UI)
            "fit_reasons": resume_job.get("fit_reasons", []),
            "rejection_reasons": resume_job.get("rejection_reasons", []),
            "compared_against": resume_job.get("compared_against", []),

            # JD education (CSV only)
            "education_match": education_match,
            "jd_min_education": jd_profile.get(
                "min_education_level", "Not specified"
            ),
        })

    # -----------------------------
    # Sort by JD score
    # -----------------------------
    ranked.sort(key=lambda x: x["score"], reverse=True)

    # -----------------------------
    # Assign ranks
    # -----------------------------
    for i, r in enumerate(ranked, start=1):
        r["rank"] = i

    return ranked
