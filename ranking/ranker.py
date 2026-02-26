from resume_parser.parser import parse_resume
from matching.scorer import score_resume

def rank_resumes(resume_paths: list, job: dict, top_k: int = None):
    """
    Rank multiple resumes against a job description

    resume_paths: list of PDF paths
    job: parsed job dictionary
    top_k: return only top K results (optional)
    """

    results = []

    for path in resume_paths:
        try:
            resume = parse_resume(path)
            score_data = score_resume(resume, job)

            results.append({
                "resume": path,
                "score": score_data["score"]
            })

        except Exception as e:
            print(f"[SKIPPED] {path} -> {e}")

    # Sort by score (descending)
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k] if top_k else results
