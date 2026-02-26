import re
import unicodedata
from analysis.education_levels import EDU_LEVELS


def normalize_text(text: str) -> str:
    # Normalize unicode (handles smart quotes, accents, etc.)
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("’", "'")
    return text.lower()


def extract_education_level(text: str) -> int:
    text = normalize_text(text)
    levels_found = []

    for key, level in EDU_LEVELS.items():
        if re.search(rf"\b{re.escape(key)}\b", text):
            levels_found.append(level)

    return max(levels_found) if levels_found else -1


def match_education(jd_level: int, resume_level: int) -> str:
    if resume_level == -1:
        return "unknown"

    if resume_level >= jd_level:
        return "meets"
    elif resume_level == jd_level - 1:
        return "partial"
    else:
        return "missing"
