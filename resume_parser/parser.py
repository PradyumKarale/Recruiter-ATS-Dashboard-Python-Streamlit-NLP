import re
from utils.pdf_utils import pdf_to_images
from utils.ocr_utils import extract_ocr_from_image
from resume_parser.rules import enhance_with_rules
from analysis.skill_normalizer import normalize_skill
from job_profile.job_loader import load_all_jobs
from analysis.education_matcher import extract_education_level

def extract_candidate_name(text: str) -> str:
    """
    Robust name extraction for OCR text.
    """
    words = text.replace("\n", " ").split()

    candidates = []
    current = []

    for w in words[:40]:  # only first part of resume
        clean = w.strip(",.").title()

        if clean.isalpha() and len(clean) > 2:
            if clean.isupper() or clean.istitle():
                current.append(clean)
            else:
                current = []
        else:
            current = []

        if 2 <= len(current) <= 4:
            candidates.append(" ".join(current))

    return candidates[0] if candidates else "Not found"



def extract_skills_from_text(text: str) -> list:
    text = text.lower()
    jobs = load_all_jobs()

    skill_vocab = set()
    for job in jobs.values():
        for group in ["critical_skills", "core_skills", "optional_skills", "soft_skills"]:
            for skill in job.get(group, []):
                skill_vocab.add(normalize_skill(skill))

    found = set()
    for skill in skill_vocab:
        if skill in text:
            found.add(skill)

    return sorted(found)

def extract_resume_experience_years(text: str) -> int:
    """
    Extracts total years of experience from resume text.
    Conservative estimate.
    """
    matches = re.findall(r"(\d+)\s*\+?\s*years", text.lower())
    if matches:
        return max(map(int, matches))
    return -1




def parse_resume(pdf_path):
    pages = pdf_to_images(pdf_path)

    all_words = []

    for page in pages:
        try:
            words, _ = extract_ocr_from_image(page)
            all_words.extend(words)
        except Exception as e:
            print(f"OCR failed on a page in {pdf_path}: {e}")
            continue

    # -----------------------------
    # TEXT PREP
    # -----------------------------
    raw_text = " ".join(all_words)
    text = raw_text.lower()

    # -----------------------------
    # INITIALIZE RESULT FIRST ✅
    # -----------------------------
    result = {
        "text": text,
        "raw_text": raw_text,
        "name": "Not found",
        "email": [],
        "phone": [],
        "skills": [],
        "education": [],
        "experience": [],
        "education_level": -1,
        "experience_years": -1,
        "sections": {}
    }

    # -----------------------------
    # RULE-BASED ENRICHMENT
    # -----------------------------
    result = enhance_with_rules(all_words, result)

    # -----------------------------
    # NAME EXTRACTION ✅ (FIXED)
    # -----------------------------
    name = extract_candidate_name(raw_text)
    result["name"] = [name] if name != "Not found" else []


    # -----------------------------
    # SKILL EXTRACTION
    # -----------------------------
    result["skills"] = extract_skills_from_text(text)

    # -----------------------------
    # EDUCATION + EXPERIENCE
    # -----------------------------
    result["education_level"] = extract_education_level(text)
    result["experience_years"] = extract_resume_experience_years(text)

    # -----------------------------
    # SECTION-AWARE TEXT
    # -----------------------------
    result["sections"] = {
        "experience": " ".join(result.get("experience", [])).lower(),
        "education": " ".join(result.get("education", [])).lower(),
        "skills": " ".join(result.get("skills", [])).lower(),
        "summary": str(result.get("name", "")).lower(),
    }

    return result
