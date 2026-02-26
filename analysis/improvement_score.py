def estimate_improvement_score(current_score, missing_skills, job_skills):
    """
    Estimate how much the resume score can improve
    if missing skills are added.
    """

    if not job_skills:
        return round(current_score, 2)

    if not missing_skills:
        return round(current_score, 2)

    # Each job skill contributes equally to the remaining score
    improvement_per_skill = (100.0 - current_score) / len(job_skills)

    potential_gain = improvement_per_skill * len(missing_skills)
    improved_score = min(100.0, current_score + potential_gain)

    return round(improved_score, 2)
