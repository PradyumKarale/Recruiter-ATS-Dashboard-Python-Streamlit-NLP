from pathlib import Path
import re

def infer_job_title(job_text: str) -> str:
    """
    Infer the most likely job title from a pasted job description.
    Uses keyword heuristics.
    """

    text = job_text.lower()

    title_keywords = {
        "Software Engineer": [
            "software engineer", "developer", "programming", "coding", "python", "java", "c++"
        ],
        "Data Scientist": [
            "data scientist", "machine learning", "ml", "statistics", "deep learning", "ai"
        ],
        "Frontend Developer": [
            "frontend", "react", "angular", "vue", "javascript", "ui", "ux"
        ],
        "Backend Developer": [
            "backend", "api", "django", "flask", "node", "spring"
        ],
        "Full Stack Developer": [
            "full stack", "frontend and backend", "mern", "mean stack"
        ],
        "Business Analyst": [
            "business analyst", "excel", "power bi", "dashboard", "reporting", "analysis"
        ],
        "Office Administrator": [
            "microsoft office", "documentation", "coordination", "time management", "teamwork"
        ],
        "HR Executive": [
            "recruitment", "human resources", "hr", "talent acquisition", "onboarding"
        ],
        "Project Manager": [
            "project management", "scrum", "agile", "stakeholders", "planning"
        ],
        "Marketing Executive": [
            "marketing", "seo", "content", "campaign", "branding", "social media"
        ]
    }

    scores = {}

    for title, keywords in title_keywords.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[title] = score

    if scores:
        # Return title with highest keyword match
        return max(scores, key=scores.get)

    return "Custom Job Description"


def parse_job_description(path: str) -> dict:
    text = Path(path).read_text(encoding="utf-8").lower()

    skills = set(re.findall(
        r"\b(microsoft office|time management|teamwork|communication|python|sql)\b",
        text
    ))

    return {
        "raw_text": text,
        "skills": list(skills)
    }

def load_all_jobs(job_dir):
    """
    Load all job descriptions from a directory.
    """
    jobs = {}

    for job_file in Path(job_dir).glob("*.txt"):
        jobs[job_file.stem] = parse_job_description(job_file)

    return jobs

def parse_job_description_from_text(text: str) -> dict:
    """
    Parse job description directly from pasted text
    (used by Streamlit UI)
    """
    text = text.lower()

    # Simple keyword-based skill extraction
    skills = set(re.findall(
        r"\b(python|java|sql|machine learning|deep learning|nlp|data science|"
        r"communication|teamwork|time management|microsoft office|excel|powerpoint|"
        r"leadership|problem solving|analysis|cloud|aws|azure)\b",
        text
    ))

    return {
        "raw_text": text,
        "skills": list(skills)
    }