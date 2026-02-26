from matching.scorer import score_resume
from analysis.skill_gap import analyze_skill_gap
from analysis.improvement_score import estimate_improvement_score


def match_resume_to_jobs(resume, jobs):
    matches = []

    for job_key, job in jobs.items():
        score_data = score_resume(resume, job)

        gap = analyze_skill_gap(
            resume_skills=resume.get("skills", []),
            job_skills=job.get("skills", [])
        )

        improvement = estimate_improvement_score(
            current_score=score_data["score"],
            missing_skills=gap["missing_skills"],
            job_skills=job.get("skills", [])
        )

        matches.append({
            "job": job_key,
            "job_title": job["title"],
            "domain": job["domain"],
            "score": score_data["score"],
            "improvement_score": improvement,
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"]
        })

    # Always return something
    if not matches:
        return []

    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches
