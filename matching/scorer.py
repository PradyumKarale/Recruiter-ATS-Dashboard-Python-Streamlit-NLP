import numpy as np
from matching.embedding_model import embed
from job_profile.skill_weights import SKILL_WEIGHTS, WEIGHT_VALUES

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b))

def score_resume(resume, job):
    resume_skills = set(map(str.lower, resume["skills"]))
    job_skills = set(map(str.lower, job["skills"]))

    total_weight = 0.0
    matched_weight = 0.0

    for category, skills in SKILL_WEIGHTS.items():
        weight = WEIGHT_VALUES[category]

        for skill in skills:
            if skill in job_skills:
                total_weight += weight
                if skill in resume_skills:
                    matched_weight += weight

    if total_weight == 0:
        score = 0.0
    else:
        score = (matched_weight / total_weight) * 100

    return {
        "score": round(score, 2),
        "matched_weight": matched_weight,
        "total_weight": total_weight
    }

