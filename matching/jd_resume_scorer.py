from functools import lru_cache
import json
from analysis.skill_gap import analyze_skill_gap
from analysis.improvement_score import estimate_improvement_score
from analysis.skill_normalizer import normalize_text_tokens, normalize_skill
from analysis.education_matcher import match_education, extract_education_level


WEIGHTS = {
    "critical_skills": 4.0,
    "core_skills": 3.0,
    "optional_skills": 1.5,
    "soft_skills": 0.5
}


def skill_confidence(skill: str, resume_text: str) -> float:
    """
    Boost score if a skill appears multiple times in resume.
    Caps boost to avoid keyword stuffing.
    """
    resume_text = resume_text.lower()
    count = resume_text.count(skill)
    return min(1.0 + 0.2 * count, 1.6)


@lru_cache(maxsize=32)
def _prepare_jd_cache(jd_key):
    """
    Cached JD skill preparation.
    jd_key must be a JSON string.
    """
    jd_profile = json.loads(jd_key)

    jd_flat_skills = []
    total_weight = 0.0

    for group, weight in WEIGHTS.items():
        for skill in jd_profile["jd_skills"].get(group, []):
            jd_flat_skills.append((skill, weight))
            total_weight += weight

    return jd_flat_skills, total_weight


def score_resume_against_jd(resume, jd_profile):
    """
    Scores a resume strictly against JD extracted keywords.
    """

    # -----------------------------
    # NORMALIZE RESUME CONTENT
    # -----------------------------
    resume_skill_set = set()

    for s in resume.get("skills", []):
        resume_skill_set.add(normalize_skill(s))

    resume_text = resume.get("text", "")
    resume_skill_set |= normalize_text_tokens(resume_text)

    # -----------------------------
    # PREPARE JD CACHE KEY
    # -----------------------------
    jd_key = {
        k: tuple(v) for k, v in jd_profile["jd_skills"].items()
    }

    jd_key = json.dumps(jd_profile, sort_keys=True)
    jd_flat_skills, total_weight = _prepare_jd_cache(jd_key)


    matched = []
    missing = []
    earned_weight = 0.0

    # -----------------------------
    # SCORING LOOP
    # -----------------------------
    for skill, weight in jd_flat_skills:

        if skill in resume_skill_set:
            confidence = skill_confidence(skill, resume_text)
            earned_weight += weight * confidence
            matched.append(skill)

        elif any(skill in token for token in resume_skill_set):
            confidence = skill_confidence(skill, resume_text)
            earned_weight += weight * 0.7 * confidence
            matched.append(skill)

        else:
            missing.append(skill)

    raw_score = earned_weight / total_weight if total_weight > 0 else 0
    score = min(round(raw_score * 100, 2), 100.0)

    improvement_score = estimate_improvement_score(
        current_score=score,
        missing_skills=missing,
        job_skills=[s for s, _ in jd_flat_skills]
    )

    return {
        "score": score,
        "matched_skills": sorted(set(matched)),
        "missing_skills": sorted(set(missing)),
        "improvement_score": min(round(improvement_score, 2), 100.0)
    }
