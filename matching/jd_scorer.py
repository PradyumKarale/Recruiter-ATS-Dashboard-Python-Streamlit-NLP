from analysis.skill_normalizer import normalize_skill, normalize_text_tokens
from analysis.education_matcher import match_education
from analysis.improvement_score import estimate_improvement_score


WEIGHTS = {
    "critical_skills": 4.0,
    "core_skills": 3.0,
    "optional_skills": 1.0,
    "soft_skills": 0.5
}


def score_resume_against_jd(resume, jd_profile):
    """
    Final ATS scorer: JD ↔ Resume (skills + experience + education)
    """

    # ---------- NORMALIZE RESUME ----------
    resume_text = resume.get("text", "").lower()

    resume_skill_set = set(
        normalize_skill(s) for s in resume.get("skills", [])
    )
    resume_skill_set |= normalize_text_tokens(resume_text)

    jd_skills = jd_profile["jd_skills"]

    matched = []
    missing = []

    total_weight = 0.0
    earned_weight = 0.0

    # ---------- SKILL MATCHING ----------
    for group, weight in WEIGHTS.items():
        for skill in jd_skills.get(group, []):
            skill = normalize_skill(skill)
            total_weight += weight

            if skill in resume_skill_set:
                earned_weight += weight
                matched.append(skill)
            else:
                missing.append(skill)

    # ---------- BASE SCORE ----------
    base_score = (earned_weight / total_weight) * 100 if total_weight > 0 else 0.0

    # ---------- EXPERIENCE BONUS ----------
    jd_years = jd_profile.get("min_experience_years", -1)
    resume_years = resume.get("experience_years", -1)

    if jd_years != -1 and resume_years != -1:
        if resume_years >= jd_years:
            base_score += 5
        elif resume_years == jd_years - 1:
            base_score += 2

    # ---------- EDUCATION BONUS / PENALTY ----------
    jd_level = jd_profile.get("min_education_level", -1)
    resume_level = resume.get("education_level", -1)

    edu_status = match_education(jd_level, resume_level)

    if edu_status == "meets":
        base_score += 5
    elif edu_status == "partial":
        base_score += 2
    elif edu_status == "missing":
        base_score -= 10

    # ---------- FINAL SCORE (SAFE CLAMP) ----------
    final_score = max(min(round(base_score, 1), 100.0), 0.0)

    improvement_score = estimate_improvement_score(
        current_score=final_score,
        missing_skills=missing,
        job_skills=sum(jd_skills.values(), [])
    )

    return {
        "score": final_score,
        "matched_skills": sorted(set(matched)),
        "missing_skills": sorted(set(missing)),
        "improvement_score": round(improvement_score, 1)
    }
