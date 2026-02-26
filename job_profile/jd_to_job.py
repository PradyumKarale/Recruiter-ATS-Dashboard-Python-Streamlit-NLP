from matching.scorer import score_resume


def infer_job_from_jd(job_text, jobs_db):
    """
    Detect which job role the recruiter wants
    based on their pasted job description.
    """

    # Convert JD into resume-like structure
    jd_resume = {
        "skills": [s.strip().lower() for s in job_text.replace("\n", ",").split(",") if len(s.strip()) > 1]
    }

    best_job = None
    best_score = -1

    for job_key, job in jobs_db.items():
        score_data = score_resume(jd_resume, job)

        if score_data["score"] > best_score:
            best_score = score_data["score"]
            best_job = {
                "job_key": job_key,
                "title": job["title"],
                "domain": job["domain"],
                "score": score_data["score"],
                "skills": job["skills"]
            }

    return best_job
