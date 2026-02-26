import re

def extract_experience_years(text: str) -> int:
    """
    Extracts minimum experience in years from text.
    Examples:
    - "0-3 years" → 0
    - "2+ years" → 2
    - "minimum 5 years" → 5
    """
    text = text.lower()

    patterns = [
        r"(\d+)\s*\+\s*years",
        r"minimum\s*(\d+)\s*years",
        r"at least\s*(\d+)\s*years",
        r"(\d+)\s*-\s*\d+\s*years",
        r"(\d+)\s*years"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    return -1  # not specified

def match_experience(jd_years: int, resume_years: int) -> str:
    if jd_years == -1:
        return "not_required"

    if resume_years == -1:
        return "unknown"

    if resume_years >= jd_years:
        return "meets"
    elif resume_years == jd_years - 1:
        return "partial"
    else:
        return "missing"
