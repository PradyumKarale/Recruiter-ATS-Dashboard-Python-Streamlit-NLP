# analysis/skill_gap.py

def analyze_skill_gap(resume_skills, job_skills):
    """
    Compare resume skills with job-required skills
    """
    resume_set = set(s.lower() for s in resume_skills)
    job_set = set(s.lower() for s in job_skills)

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)

    return {
        "matched_skills": matched,
        "missing_skills": missing
    }
