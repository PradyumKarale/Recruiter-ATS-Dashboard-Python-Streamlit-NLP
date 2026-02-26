from analysis.finance_skill_inference import FINANCE_INFERENCE_MAP
from analysis.skill_normalizer import normalize_skill

def enrich_finance_skills(resume):
    """
    Adds inferred finance skills based on resume text.
    Soft enrichment only.
    """
    text = resume.get("text", "").lower()
    inferred = set()

    for phrase, implied_skill in FINANCE_INFERENCE_MAP.items():
        if phrase in text:
            inferred.add(normalize_skill(implied_skill))

    return inferred
