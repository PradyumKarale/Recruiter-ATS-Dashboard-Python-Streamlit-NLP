# analysis/skill_normalizer.py

import re

CANONICAL_SKILLS = {
    # --- Frontend ---
    "html5": "html",
    "css3": "css",
    "react.js": "react",
    "reactjs": "react",

    # --- JavaScript ---
    "js": "javascript",
    "java script": "javascript",

    # --- Backend / APIs ---
    "restapi": "rest api",
    "restapis": "rest api",
    "apiintegration": "api integration",

    # --- Node ---
    "node.js": "nodejs",
    "node": "nodejs",

    # --- DevOps ---
    "cicd": "ci cd",
    "ci/cd": "ci cd",

    # --- Databases ---
    "postgres": "postgresql",
    "postgre": "postgresql",

    # --- Typescript ---
    "ts": "typescript",
}

CANONICAL_SKILLS.update({
    # Finance
    "p&l": "profitandloss",
    "profit loss": "profitandloss",
    "profit and loss": "profitandloss",

    "finalization of books": "financialstatements",
    "financial reporting": "financialstatements",
    "balance sheet": "financialstatements",

    "gst filing": "taxation",
    "income tax": "taxation",
    "tax returns": "taxation",

    "accounts payable": "accountspayable",
    "accounts receivable": "accountsreceivable",

    "book keeping": "accounting",
    "bookkeeping": "accounting"
})


def normalize_skill(skill: str) -> str:
    if not skill:
        return ""

    skill = skill.lower().strip()

    # normalize punctuation but KEEP SPACES FIRST
    skill = re.sub(r"[^a-z0-9+.# ]", "", skill)

    # collapse spaces AFTER canonical lookup
    collapsed = skill.replace(" ", "")

    # try collapsed form first
    if collapsed in CANONICAL_SKILLS:
        return CANONICAL_SKILLS[collapsed]

    # fallback to spaced form
    return CANONICAL_SKILLS.get(skill, skill)


def normalize_text_tokens(text: str) -> set:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+.# ]", " ", text)

    tokens = set()
    words = text.split()

    for w in words:
        tokens.add(normalize_skill(w))

    # also try joining neighbors (OCR safety)
    for i in range(len(words) - 1):
        joined = words[i] + words[i + 1]
        tokens.add(normalize_skill(joined))

    return tokens
