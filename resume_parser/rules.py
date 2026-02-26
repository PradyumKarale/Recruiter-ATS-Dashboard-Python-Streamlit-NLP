import re
from pathlib import Path

# Always resolve relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILL_FILE = PROJECT_ROOT / "Resume_data" / "skills_master.txt"

def load_skills():
    return {
        line.strip().lower()
        for line in SKILL_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }

SKILLS = load_skills()

NORMALIZATION = {
    "ml": "machine learning",
    "dl": "deep learning",
    "ai": "artificial intelligence",
    "py": "python",
    "tf": "tensorflow",
    "torch": "pytorch",
}

def normalize(text: str) -> str:
    text = text.lower()
    for k, v in NORMALIZATION.items():
        text = re.sub(rf"\b{k}\b", v, text)
    return text


def enhance_with_rules(words, result):
    text = " ".join(words).lower()

    result.setdefault("email", [])
    result.setdefault("phone", [])
    result.setdefault("skills", [])
    result.setdefault("name", [])
    result.setdefault("education", [])
    result.setdefault("experience", [])

    # Email
    result["email"] = list(set(
        re.findall(
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            text.replace(" ", "")
        )
    ))

    # Phone
    result["phone"] = list(set(
        re.findall(r"\+?\d[\d\s\-\(\)]{8,}\d", text)
    ))

    # Skills
    normalized_text = normalize(text)

    print("\n--- DEBUG TEXT SAMPLE ---")
    print(normalize(text)[:500])
    print("--- END DEBUG TEXT ---\n")


    found_skills = set()

    for skill in SKILLS:
        skill_norm = normalize(skill)
        if skill_norm in normalized_text:
            found_skills.add(skill)

    result["skills"] = sorted(found_skills)

    return result   # 🔑 REQUIRED
