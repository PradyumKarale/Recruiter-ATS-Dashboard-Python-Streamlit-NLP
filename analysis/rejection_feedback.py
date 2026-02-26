def generate_rejection_feedback(
    resume_name: str,
    score: float,
    matched_skills: list,
    missing_skills: list,
    threshold: float
) -> dict:
    """
    Generates structured feedback for rejected or borderline resumes
    """

    status = "Shortlisted" if score >= threshold else "Rejected"

    suggestions = []

    if missing_skills:
        suggestions.append(
            f"Add missing skills explicitly: {', '.join(missing_skills)}"
        )

    if score < threshold:
        suggestions.append(
            "Improve keyword alignment with the job description"
        )
        suggestions.append(
            "Place skills in a dedicated SKILLS section"
        )
        suggestions.append(
            "Use ATS-friendly formatting (simple headings, no tables)"
        )

    return {
        "resume": resume_name,
        "status": status,
        "score": round(score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions
    }
